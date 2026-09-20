"""
CKI Utility Functions
======================
General-purpose helpers for the CKI computational framework.
"""

import numpy as np


def ensure_probability_distribution(
    x: np.ndarray,
    epsilon: float = 1e-9,
    mode: str = "softmax",
) -> np.ndarray:
    """
    Normalize a vector to a valid probability distribution (sum = 1).

    Parameters
    ----------
    x : np.ndarray
        Input vector (1D).
    epsilon : float
        Small constant to avoid division by zero.
    mode : str
        How to convert to a probability distribution:
        - "softmax": always use softmax (appropriate for log1p-transformed data). **Default.**
        - "auto": use softmax if any value is negative, otherwise normalize by sum.
        - "normalize": normalize by sum, after clipping negatives to 0 (legacy behavior).

    Returns
    -------
    np.ndarray
        Normalized probability distribution with sum = 1.
        Falls back to uniform distribution if input sum is zero.
    """
    x = np.asarray(x, dtype=float)

    if mode == "auto":
        mode = "softmax" if (x < 0).any() else "normalize"

    if mode == "softmax":
        # log1p-transformed values: convert via softmax
        x_max = x.max()
        exp_x = np.exp(x - x_max)  # subtract max for numerical stability
        return exp_x / (exp_x.sum() + epsilon)

    # normalize mode (legacy, for non-negative raw counts)
    x = np.maximum(x, 0)  # ensure non-negative
    x_sum = x.sum()
    if x_sum > 0:
        return x / x_sum
    # fall back to uniform distribution
    return np.ones_like(x) / len(x)
