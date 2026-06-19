"""SkyDiscover evaluator for MIMO channel estimation.

Ported from the-ai-telco-engineer/tasks/channel_estimation/eval/eval.py.

Scores a candidate ``mimo_detector(y, no)`` by Normalized Validation Error (NVE):
the mean ratio of the candidate's BLER to the perfect-CSI BLER over a range of
SNRs (4x16 MIMO OFDM uplink, 3GPP UMi channel, 5G LDPC, QPSK).

Lower NVE is better, but SkyDiscover MAXIMIZES ``combined_score``, so we report::

    combined_score = 1.0 / NVE        (failures -> 0.0, which is always worst)

and also expose the raw ``nve`` metric for the dashboard. ``mimo_nve()`` is a
pure helper (no SkyDiscover dependency) so a containerized wrapper can reuse the
exact same simulation.
"""
import os
import sys
import json
import pickle
import importlib.util
import traceback
from contextlib import redirect_stdout
from threading import RLock

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)  # so link_config + the candidate's imports resolve

if os.getenv("CUDA_VISIBLE_DEVICES") is None:
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

_MPLCONFIGDIR = os.path.join(os.environ.get("TMPDIR", "/tmp"), "matplotlib-skydiscover")
os.makedirs(_MPLCONFIGDIR, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", _MPLCONFIGDIR)
os.environ.setdefault("MPLBACKEND", "Agg")

# torch.compile's Inductor CPU backend needs a C++ compiler (gcc/cl.exe) to build
# kernels. The telco repo gets this from its Linux Docker image; on a bare Windows
# host cl.exe is usually absent, so disable Dynamo and run eagerly. Set
# TORCHDYNAMO_DISABLE=0 to re-enable compilation where a compiler is available.
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")

import torch
import numpy as np
import sionna.phy
sionna.phy.config.seed = 42

import logging
logging.getLogger("torch._dynamo").setLevel(logging.ERROR)

from sionna.phy import Block
from sionna.phy.ofdm import ResourceGridMapper
from sionna.phy.channel.tr38901 import AntennaArray, UMi, Antenna
from sionna.phy.channel import OFDMChannel, gen_single_sector_topology
from sionna.phy.fec.ldpc import LDPC5GEncoder, LDPC5GDecoder
from sionna.phy.mapping import Mapper, BinarySource
from sionna.phy.utils import ebnodb2no, sim_ber

from link_config import (
    NUM_TX_ANT, NUM_UT, NUM_RX_ANT, NUM_BITS_PER_SYMBOL, NUM_OFDM_SYMBOLS,
    CODERATE, CARRIER_FREQUENCY, SM, RG,
)

# --- Simulation parameters (match the telco channel_estimation task) ---------
SNR_RANGE = (-9.0, -2.0, 1.0)  # (start, stop, step) in dB
BATCH_SIZE = 10
MAX_MC_ITER = 1000
NUM_TARGET_BLOCK_ERRORS = 1000
TARGET_BLER = 1e-3
SPEED = 3.0  # UE speed in m/s
_BLER_PERF_CSI = os.path.join(_HERE, "bler_perf_csi.pkl")
_BASELINE_PROGRAM = os.path.join(_HERE, "initial_program.py")
_CURVE_LOCK = RLock()
_BASELINE_ATTEMPTED = False
_BASELINE_BLER = None
_BEST_SCORE = float("-inf")
_BEST_PROGRAM_BLER = None


class MIMOModel(Block):
    """4x16 MIMO OFDM uplink (UMi channel, 5G LDPC, QPSK) wrapping the candidate
    detector. Verbatim from the telco eval, minus the file loader."""

    def __init__(self, detector_fn):
        super().__init__()
        self._detector_fn = detector_fn
        self._num_ut = NUM_UT
        self._num_streams_per_tx = NUM_TX_ANT
        self._num_bits_per_symbol = NUM_BITS_PER_SYMBOL
        self._coderate = CODERATE
        self._rg = RG
        self._sm = SM
        self._n = int(self._rg.num_data_symbols * self._num_bits_per_symbol)
        self._k = int(self._n * self._coderate)

        self._ut_array = Antenna(
            polarization="single", polarization_type="V",
            antenna_pattern="omni", carrier_frequency=CARRIER_FREQUENCY,
        )
        self._bs_array = AntennaArray(
            num_rows=1, num_cols=int(NUM_RX_ANT / 2),
            polarization="dual", polarization_type="cross",
            antenna_pattern="38.901", carrier_frequency=CARRIER_FREQUENCY,
        )
        self._umi = UMi(
            carrier_frequency=CARRIER_FREQUENCY, o2i_model="low",
            ut_array=self._ut_array, bs_array=self._bs_array, direction="uplink",
        )
        self._channel = OFDMChannel(
            self._umi, self._rg, normalize_channel=True, return_channel=False,
        )

        self._binary_source = BinarySource()
        self._encoder = LDPC5GEncoder(self._k, self._n)
        self._mapper = Mapper("qam", self._num_bits_per_symbol)
        self._rg_mapper = ResourceGridMapper(self._rg)
        self._decoder = LDPC5GDecoder(self._encoder, hard_out=True)

    @torch.compile
    def call(self, batch_size, ebno_db):
        no = ebnodb2no(ebno_db, self._num_bits_per_symbol, self._coderate, self._rg)

        # Transmitter
        b = self._binary_source([batch_size, self._num_ut, self._num_streams_per_tx, self._k])
        c = self._encoder(b)
        x = self._mapper(c)
        x_rg = self._rg_mapper(x)

        # Channel
        topology = gen_single_sector_topology(
            batch_size, self._num_ut, "umi", max_ut_velocity=SPEED,
        )
        self._umi.set_topology(*topology)
        y = self._channel(x_rg, no)

        # Candidate detector (channel estimation + equalization + demapping)
        llr = self._detector_fn(y, no)
        llr = torch.reshape(llr, [batch_size, self._num_ut, self._num_streams_per_tx, self._n])

        # Decoding
        b_hat = self._decoder(llr)
        return b, b_hat


def _load_detector(program_path):
    name = "_cand_" + os.path.splitext(os.path.basename(program_path))[0]
    spec = importlib.util.spec_from_file_location(name, program_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {program_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def to_float_list(values):
    """Convert tensors/arrays/sequences/scalars to JSON- and matplotlib-friendly floats."""
    if values is None:
        return None
    if hasattr(values, "detach"):
        values = values.detach().cpu().numpy()
    elif hasattr(values, "cpu"):
        values = values.cpu().numpy()
    if hasattr(values, "tolist"):
        values = values.tolist()
    if isinstance(values, (list, tuple)):
        return [float(v) for v in values]
    return [float(values)]


def _to_float_list(values):
    return to_float_list(values)


def _algorithm_name():
    return os.environ.get("ALGORITHM_NAME") or "unknown_algorithm"


def _algorithm_output_dir(output_dir=None, algorithm_name=None):
    base_dir = output_dir or _output_dir()
    algorithm_name = algorithm_name or _algorithm_name()
    return os.path.join(base_dir or ".", algorithm_name)


def save_current_bler_json(
    path,
    snr_db_done,
    candidate_bler,
    perfect_snr_db,
    perfect_csi_bler=None,
    baseline_bler=None,
    algorithm_name=None,
):
    data = {
        "algorithm_name": algorithm_name or _algorithm_name(),
        "snr_db_done": to_float_list(snr_db_done) or [],
        "candidate_bler": to_float_list(candidate_bler) or [],
        "perfect_snr_db": to_float_list(perfect_snr_db) or [],
        "perfect_csi_bler": to_float_list(perfect_csi_bler),
        "baseline_bler": to_float_list(baseline_bler),
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def plot_current_bler(
    path,
    snr_db_done,
    candidate_bler,
    perfect_snr_db,
    perfect_csi_bler=None,
    baseline_bler=None,
    algorithm_name=None,
):
    snr_db_done = to_float_list(snr_db_done) or []
    candidate_bler = to_float_list(candidate_bler) or []
    perfect_snr_db = to_float_list(perfect_snr_db) or []
    perfect_csi_bler = to_float_list(perfect_csi_bler)
    baseline_bler = to_float_list(baseline_bler)
    algorithm_name = algorithm_name or _algorithm_name()

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plotted_any = False
    plt.figure(figsize=(8, 5))

    if perfect_csi_bler is None:
        print("Warning: missing BLER curve for Perfect CSI / Genie; skipping plot curve.")
    elif len(perfect_csi_bler) != len(perfect_snr_db):
        print(
            "Warning: Perfect CSI / Genie BLER curve has "
            f"{len(perfect_csi_bler)} points, but SNR list has {len(perfect_snr_db)}; "
            "skipping plot curve."
        )
    else:
        plt.plot(perfect_snr_db, perfect_csi_bler, marker="o", label="Perfect CSI / Genie")
        plotted_any = True

    if baseline_bler is None:
        print("Warning: missing BLER curve for Baseline; skipping plot curve.")
    elif len(baseline_bler) != len(perfect_snr_db):
        print(
            f"Warning: Baseline BLER curve has {len(baseline_bler)} points, "
            f"but SNR list has {len(perfect_snr_db)}; skipping plot curve."
        )
    else:
        plt.plot(perfect_snr_db, baseline_bler, marker="o", label="Baseline")
        plotted_any = True

    if not candidate_bler:
        print("Warning: missing BLER curve for Current Candidate; skipping plot curve.")
    elif len(candidate_bler) != len(snr_db_done):
        print(
            f"Warning: Current Candidate BLER curve has {len(candidate_bler)} points, "
            f"but completed SNR list has {len(snr_db_done)}; skipping plot curve."
        )
    else:
        plt.plot(snr_db_done, candidate_bler, marker="o", label="Current Candidate")
        plotted_any = True

    if not plotted_any:
        print("Warning: no BLER curves available to plot.")

    plt.yscale("log")
    plt.xlabel("SNR (dB)")
    plt.ylabel("BLER")
    plt.title(f"{algorithm_name}: Current Candidate BLER vs SNR")
    if plotted_any:
        plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def update_current_bler_plot(
    output_dir,
    snr_db_done,
    candidate_bler,
    perfect_snr_db,
    perfect_csi_bler=None,
    baseline_bler=None,
    algorithm_name=None,
):
    algorithm_name = algorithm_name or _algorithm_name()
    out_dir = _algorithm_output_dir(output_dir, algorithm_name)
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "bler_vs_snr_current.json")
    png_path = os.path.join(out_dir, "bler_vs_snr_current.png")
    save_current_bler_json(
        json_path,
        snr_db_done,
        candidate_bler,
        perfect_snr_db,
        perfect_csi_bler=perfect_csi_bler,
        baseline_bler=baseline_bler,
        algorithm_name=algorithm_name,
    )
    plot_current_bler(
        png_path,
        snr_db_done,
        candidate_bler,
        perfect_snr_db,
        perfect_csi_bler=perfect_csi_bler,
        baseline_bler=baseline_bler,
        algorithm_name=algorithm_name,
    )


def plot_bler_vs_snr(
    snr_db,
    perfect_csi_bler=None,
    baseline_bler=None,
    best_program_bler=None,
    output_dir=".",
    algorithm_name=None,
):
    """Save BLER-vs-SNR diagnostics without affecting evaluator scoring."""
    snr_db = _to_float_list(snr_db)
    curves = {
        "Perfect CSI / Genie": _to_float_list(perfect_csi_bler),
        "Baseline": _to_float_list(baseline_bler),
        "Best Program": _to_float_list(best_program_bler),
    }

    algorithm_name = algorithm_name or _algorithm_name()
    output_dir = _algorithm_output_dir(output_dir, algorithm_name)
    os.makedirs(output_dir or ".", exist_ok=True)
    json_path = os.path.join(output_dir or ".", "bler_vs_snr.json")
    png_path = os.path.join(output_dir or ".", "bler_vs_snr.png")

    with open(json_path, "w") as f:
        json.dump(
            {
                "algorithm_name": algorithm_name,
                "snr_db": snr_db,
                "perfect_csi_bler": curves["Perfect CSI / Genie"],
                "baseline_bler": curves["Baseline"],
                "best_program_bler": curves["Best Program"],
            },
            f,
            indent=2,
        )

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plotted_any = False
    plt.figure(figsize=(8, 5))
    for label, values in curves.items():
        if values is None:
            print(f"Warning: missing BLER curve for {label}; skipping plot curve.")
            continue
        if len(values) != len(snr_db):
            print(
                f"Warning: BLER curve for {label} has {len(values)} points, "
                f"but SNR list has {len(snr_db)}; skipping plot curve."
            )
            continue
        plt.plot(snr_db, values, marker="o", label=label)
        plotted_any = True

    if not plotted_any:
        print("Warning: no BLER curves available to plot.")

    plt.yscale("log")
    plt.xlabel("SNR (dB)")
    plt.ylabel("BLER")
    plt.title(f"{algorithm_name}: BLER vs SNR")
    if plotted_any:
        plt.legend()
    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(png_path, dpi=150)
    plt.close()


def _load_perfect_csi_bler():
    try:
        with open(_BLER_PERF_CSI, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Warning: failed to load perfect-CSI BLER curve: {e}")
        return None


def _simulate_program_bler(program_path, update_current_plot=False, output_dir=None, baseline_bler=None):
    """Run the Sionna BLER simulation and return the raw BLER curve plus NVE."""
    module = _load_detector(program_path)
    if not callable(getattr(module, "mimo_detector", None)):
        raise ValueError("program must define a callable mimo_detector(y, no)")

    model = MIMOModel(module.mimo_detector)
    snr_points = np.arange(SNR_RANGE[0], SNR_RANGE[1], SNR_RANGE[2])
    bler_perf_csi = _load_perfect_csi_bler()
    if bler_perf_csi is None:
        raise ValueError("perfect-CSI BLER curve is unavailable")

    if not update_current_plot:
        # Fast path for normal/no-plot runs: keep all SNRs in one sim_ber call.
        # Splitting by SNR is only needed for live plotting side effects.
        with open(os.devnull, "w") as devnull, redirect_stdout(devnull):
            _, bler = sim_ber(
                model,
                snr_points,
                batch_size=BATCH_SIZE,
                max_mc_iter=MAX_MC_ITER,
                num_target_block_errors=NUM_TARGET_BLOCK_ERRORS,
                target_bler=TARGET_BLER,
            )
        bler = np.array(to_float_list(bler), dtype=float)
    else:
        candidate_bler = []
        for snr_db in snr_points:
            # Suppress sim_ber's verbose progress output while preserving one sim_ber call per SNR.
            with open(os.devnull, "w") as devnull, redirect_stdout(devnull):
                _, bler_at_snr = sim_ber(
                    model,
                    np.array([snr_db]),
                    batch_size=BATCH_SIZE,
                    max_mc_iter=MAX_MC_ITER,
                    num_target_block_errors=NUM_TARGET_BLOCK_ERRORS,
                    target_bler=TARGET_BLER,
                )
            bler_value = to_float_list(bler_at_snr)[0]
            candidate_bler.append(bler_value)
            try:
                update_current_bler_plot(
                    output_dir=output_dir,
                    snr_db_done=snr_points[: len(candidate_bler)],
                    candidate_bler=candidate_bler,
                    perfect_snr_db=snr_points,
                    perfect_csi_bler=bler_perf_csi,
                    baseline_bler=baseline_bler,
                )
            except Exception as e:
                print(f"Warning: failed to update current BLER-vs-SNR plot/data: {e}")

        bler = np.array(candidate_bler, dtype=float)

    # Discard SNR points where perfect-CSI BLER is 0 (avoid divide-by-zero).
    nz = bler_perf_csi > 0
    nve = float(np.mean(bler[nz] / bler_perf_csi[nz]))
    if not np.isfinite(nve) or nve <= 0:
        raise ValueError(f"non-finite NVE: {nve}")

    return snr_points, bler, bler_perf_csi, nve


def _get_baseline_bler():
    """Compute the default LS-estimator baseline once per evaluator process."""
    global _BASELINE_ATTEMPTED, _BASELINE_BLER
    with _CURVE_LOCK:
        if _BASELINE_ATTEMPTED:
            return _BASELINE_BLER
        _BASELINE_ATTEMPTED = True

    try:
        _, baseline_bler, _, _ = _simulate_program_bler(_BASELINE_PROGRAM)
    except Exception as e:
        print(f"Warning: failed to compute baseline BLER curve: {e}")
        baseline_bler = None

    with _CURVE_LOCK:
        _BASELINE_BLER = baseline_bler
        return _BASELINE_BLER


def _update_best_program_curve(score, bler):
    global _BEST_SCORE, _BEST_PROGRAM_BLER
    with _CURVE_LOCK:
        if score >= _BEST_SCORE:
            _BEST_SCORE = score
            _BEST_PROGRAM_BLER = bler
        return _BEST_PROGRAM_BLER


def _output_dir():
    return os.environ.get("SKYDISCOVER_OUTPUT_DIR") or os.getcwd()


def _plots_disabled():
    value = os.environ.get("DISABLE_BLER_PLOTS", "")
    return value.lower() in {"1", "true", "yes", "on"}


def mimo_nve(program_path):
    """Run the Sionna BLER simulation for one candidate.

    Returns ``(ok: bool, nve: float, message: str)``. Pure -- no SkyDiscover
    imports -- so a container wrapper can reuse it.
    """
    try:
        _, _, _, nve = _simulate_program_bler(program_path)
        return True, nve, f"NVE={nve:.4f}"
    except Exception as e:
        return False, float("inf"), f"runtime error: {e}\n{traceback.format_exc()}"


def evaluate(program_path):
    """SkyDiscover Python-evaluator entry point."""
    snr_points = np.arange(SNR_RANGE[0], SNR_RANGE[1], SNR_RANGE[2])
    bler = None
    bler_perf_csi = _load_perfect_csi_bler()
    try:
        snr_points, bler, bler_perf_csi, nve = _simulate_program_bler(
            program_path,
            update_current_plot=not _plots_disabled(),
            output_dir=_output_dir(),
            baseline_bler=_BASELINE_BLER,
        )
        ok = True
        msg = f"NVE={nve:.4f}"
    except Exception as e:
        ok = False
        nve = float("inf")
        msg = f"runtime error: {e}\n{traceback.format_exc()}"

    metrics = {
        "combined_score": (1.0 / nve) if ok else 0.0,  # higher is better
        "nve": nve if ok else 1e9,                      # lower is better (true metric)
        "valid": 1.0 if ok else 0.0,
    }

    baseline_bler = _get_baseline_bler()
    if ok:
        best_program_bler = _update_best_program_curve(metrics["combined_score"], bler)
    else:
        best_program_bler = _BEST_PROGRAM_BLER

    if not _plots_disabled():
        try:
            plot_bler_vs_snr(
                snr_points,
                perfect_csi_bler=bler_perf_csi,
                baseline_bler=baseline_bler,
                best_program_bler=best_program_bler,
                output_dir=_output_dir(),
            )
        except Exception as e:
            print(f"Warning: failed to save BLER-vs-SNR plot/data: {e}")

    try:
        # Attach feedback so it is injected into the next prompt as context.
        from skydiscover.evaluation.evaluation_result import EvaluationResult
        return EvaluationResult(metrics=metrics, artifacts={"feedback": msg})
    except Exception:
        return metrics  # standalone fallback (e.g. running outside SkyDiscover)


if __name__ == "__main__":
    # Quick self-test: python evaluator.py [program.py]
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "initial_program.py")
    result = evaluate(path)
    try:
        print(result.to_dict())
    except AttributeError:
        print(result)
