<p align="center"><strong>HUBA</strong> &middot; <em>FPGA-based probabilistic computer</em></p>

---

# Matrix animation viewer

> Plays the emulator's frame-by-frame output as a minimal matrix animation; for anyone running or adapting the emulator.

| Field  | Value                         |
|--------|-------------------------------|
| Status | Draft                         |
| Date   | 2026-11-22                    |
| Author | Emilia Łukasiuk               |

## Purpose

This tool reads a .npy file written by the emulator and displays it as an animated matrix. The viewer only reads the file; it does not generate or modify the data.

## Details

### Input file

- File type: `.npy`
- Shape: `(frames, rows, cols)` or `(frames, n)` where a 2D array is shown as one row per frame
- Values: `+1/-1`, or `1/0` where `0` means `-1`
- Frame 0 is the starting state
- A wrong shape or other values give an `error:` message and exit code 1

### Writing the file from the emulator

The emulator does not write this file yet and will be adapted on its own branch:

```python
import numpy as np

frames = []  # one list of rows per step, each cell +1 or -1
# after every step of the emulator:
frames.append([[bit.value for bit in row] for row in grid])
# at the end of the run:
np.save("run.npy", np.array(frames, dtype=np.int8))
```

A Max-Cut state vector per step works too: save an array of shape `(frames, n)`.

### Run

```bash
python3 -m tools.viz run.npy
python3 -m tools.viz run.npy --interval 60 --decay 0.8
python3 -m tools.viz run.npy --save run.gif
python3 -m tools.viz run.npy --save run.mp4
```

- The window loops until it is closed, or `q` or `Esc` is pressed
- Space pauses and resumes
- `--interval` is milliseconds per frame (default 120)
- `--decay` is how fast the flip afterglow fades, 0 up to below 1 (default 0.6)
- `--save` writes a `.gif` (needs Pillow) or `.mp4` (needs ffmpeg) and opens no window

### Look

Dark background with no axes, only the matrix and a small `frame / last` counter. Two calm colours for `+1` and `-1`. A cell that flipped since the previous frame flashes bright and fades back over a few frames. The colours are the constants `BACKGROUND`, `TEXT`, `PLUS`, `MINUS` and `GLOW` at the top of `tools/viz/frames.py`.

### Requirements

- NumPy and matplotlib
- Pillow to save a GIF
- The ffmpeg program to save an MP4
- Install with `python3 -m pip install numpy matplotlib pillow`
- Tests: from `src/`, `python3 -m unittest discover -s tests`

## References

- [1] tools/emulator/main.py (the emulator whose output this plays)
- [2] tools/viz/cli.py (the command line)

---

<p align="center"><sub><strong>HUBA</strong> &middot; Licensed under the Apache License 2.0 &middot; see the <code>LICENSE</code> file in the repository root</sub></p>
