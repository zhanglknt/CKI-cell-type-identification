"""
CKI Utility Functions
======================
General-purpose helpers for the CKI computational framework.
"""

import warnings

import numpy as np

# Additive epsilon used ONLY inside probability-distribution
# normalization (ensure_probability_distribution) to keep the
# denominator well-defined. Never applied to k_n / k_f / omega.
# See the numerical-guards block at the top of cki.core for the
# unified documentation of all guard conventions in the package.
_EPS = 1e-9

# Densification guard: converting a sparse matrix with more than this
# many elements to dense (> ~800 MB as float64) emits a warning so a
# potential OOM is never silent. See densify().
_DENSIFY_WARN_THRESHOLD = 1e8


def densify(X, context: str = "expression matrix") -> np.ndarray:
    """Convert a (possibly sparse) matrix to a dense float ndarray.

    Emits a :class:`UserWarning` when a sparse matrix exceeds
    ``_DENSIFY_WARN_THRESHOLD`` elements (or nonzeros), because
    densifying matrices of that scale can exhaust memory. The
    conversion is still performed; the warning only makes the risk
    visible instead of failing silently with an OOM.

    Parameters
    ----------
    X : array-like or scipy sparse matrix
        Matrix to densify.
    context : str
        Short description included in the warning message.
    """
    if hasattr(X, "toarray"):
        n_elements = X.shape[0] * X.shape[1]
        nnz = getattr(X, "nnz", 0)
        if n_elements > _DENSIFY_WARN_THRESHOLD or nnz > _DENSIFY_WARN_THRESHOLD:
            warnings.warn(
                f"Densifying a sparse {context} of shape {X.shape} "
                f"({n_elements:.2e} elements, {nnz:.2e} nonzeros); "
                f"the dense array may require "
                f"~{n_elements * 8 / 1e9:.1f} GB of memory (float64).",
                UserWarning,
                stacklevel=2,
            )
        X = X.toarray()
    return np.asarray(X, dtype=float)


def ensure_probability_distribution(
    x: np.ndarray,
    epsilon: float = _EPS,
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
