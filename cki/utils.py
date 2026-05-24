"""
CKI Utility Functions
======================
General-purpose helpers for the CKI computational framework.
"""

import numpy as np


def ensure_probability_distribution(
    x: np.ndarray,
    epsilon: float = 1e-10,
) -> np.ndarray:
    """
    Normalize a vector to a valid probability distribution (sum = 1).

    Ensures non-negativity and handles edge cases gracefully.

    Parameters
    ----------
    x : np.ndarray
        Input vector (1D).
    epsilon : float
        Small constant to avoid division by zero.

    Returns
    -------
    np.ndarray
        Normalized probability distribution with sum = 1.
        Falls back to uniform distribution if input sum is zero.
    """
    x = np.asarray(x, dtype=float)
    x = np.maximum(x, 0)  # ensure non-negative
    x_sum = x.sum()
    if x_sum > 0:
        return x / x_sum
    # fall back to uniform distribution
    return np.ones_like(x) / len(x)
