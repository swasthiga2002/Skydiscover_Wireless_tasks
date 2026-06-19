"""Compatibility entry point for running the channel-estimation evaluator."""
import os
import sys

from evaluator import _HERE, evaluate


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "initial_program.py")
    result = evaluate(path)
    try:
        print(result.to_dict())
    except AttributeError:
        print(result)
