"""Seed program for the SkyDiscover channel-estimation task.

SkyDiscover only mutates the code inside the EVOLVE-BLOCK markers -- i.e. the
channel estimator. The LMMSE equalizer + APP demapper and the detector wiring
are fixed scaffold (the task requires using Sionna's LMMSE equalizer and APP
demapper).

`link_config.py` sits next to evaluator.py, which SkyDiscover puts on sys.path,
so these imports resolve at evaluation time.
"""
from sionna.phy.ofdm import LSChannelEstimator, LMMSEEqualizer
from sionna.phy.mapping import Demapper
from link_config import RG, SM, NUM_BITS_PER_SYMBOL

_lmmse_equ = LMMSEEqualizer(RG, SM)
_demapper = Demapper("app", "qam", NUM_BITS_PER_SYMBOL)

# EVOLVE-BLOCK-START
# Improve this channel estimator to MINIMIZE NVE. Do NOT just call Sionna's
# built-in LS/LMMSE estimators. estimate_channel must return:
#   h_hat:   [batch, num_rx, num_rx_ant, num_tx, num_streams_per_tx, num_ofdm_symbols, fft_size] complex64
#   err_var: same shape, float32
_ls_est = LSChannelEstimator(RG, interpolation_type="lin_time_avg")


def estimate_channel(y, no):
    h_hat, err_var = _ls_est(y, no)
    return h_hat, err_var
# EVOLVE-BLOCK-END


def mimo_detector(y, no):
    h_hat, err_var = estimate_channel(y, no)
    x_hat, no_eff = _lmmse_equ(y, h_hat, err_var, no)
    llr = _demapper(x_hat, no_eff)
    return llr
