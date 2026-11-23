"""Load emulator output and turn it into per-frame colours for the viewer."""
import os

import numpy as np

# The whole colour scheme lives here; change these to restyle the viewer.
BACKGROUND = "#0b0d12"
TEXT = "#7d8597"
PLUS = (0.89, 0.67, 0.38)
MINUS = (0.16, 0.21, 0.31)
GLOW = (0.97, 0.95, 0.90)


def load_frames(source):
    """Return the spins as an int8 array of shape (frames, rows, cols) holding +1/-1.

    source is a path (str or os.PathLike) to a .npy file, or an array-like. Values
    may be +1/-1 or 1/0 (0 means -1). A 2D array (frames, n) becomes one row per frame.
    """
    if isinstance(source, (str, os.PathLike)):
        arr = np.asarray(np.load(source, allow_pickle=False))
    else:
        arr = np.asarray(source)

    if arr.ndim == 2:
        arr = arr.reshape(arr.shape[0], 1, arr.shape[1])
    elif arr.ndim != 3:
        raise ValueError(f"expected shape (frames, rows, cols) or (frames, n), got {arr.shape}")
    if arr.size == 0:
        raise ValueError("no frames or no cells in the input")

    values = set(np.unique(arr).tolist())
    if not (values <= {-1, 1} or values <= {0, 1}):
        raise ValueError("values must be all +1/-1 or all 1/0")
    return np.where(arr > 0, 1, -1).astype(np.int8)


def glow_levels(spins, decay=0.6):
    """Return afterglow levels in [0, 1], same shape as spins.

    A cell that differs from the previous frame is 1.0; every other cell fades by
    `decay` per frame. Frame 0 has no previous frame, so it is all 0.
    """
    if not 0 <= decay < 1:
        raise ValueError("decay must be at least 0 and below 1")

    glow = np.zeros(spins.shape, dtype=float)
    for t in range(1, len(spins)):
        flipped = spins[t] != spins[t - 1]
        # A cell that flips again restarts at 1.0.
        glow[t] = np.where(flipped, 1.0, glow[t - 1] * decay)
    return glow


def frame_colors(spins, decay=0.6):
    """Return RGB floats of shape (frames, rows, cols, 3): PLUS or MINUS blended toward GLOW."""
    glow = glow_levels(spins, decay)[..., None]
    base = np.where(spins[..., None] > 0, PLUS, MINUS)
    return base * (1 - glow) + np.array(GLOW) * glow
