"""Command line for the matrix viewer: play an emulator .npy file or save it as GIF/MP4."""
import argparse
import os
import sys

import matplotlib.pyplot as plt
from matplotlib import animation

from tools.viz.anim import build_animation
from tools.viz.frames import load_frames


def _make_writer(path, interval_ms):
    """Return the matplotlib writer for the path's extension, or raise why there is none."""
    if interval_ms <= 0:
        raise ValueError("interval_ms must be positive")
    ext = os.path.splitext(str(path))[1].lower()
    fps = 1000.0 / interval_ms

    if ext == ".gif":
        return animation.PillowWriter(fps=fps)
    if ext == ".mp4":
        if not animation.FFMpegWriter.isAvailable():
            raise RuntimeError("ffmpeg not found: install ffmpeg or save a .gif instead")
        return animation.FFMpegWriter(fps=fps)
    raise ValueError(f"--save supports .gif or .mp4, got {ext!r}")


def save_animation(anim, path, interval_ms):
    """Write the animation to a .gif (Pillow) or .mp4 (ffmpeg) file."""
    anim.save(path, writer=_make_writer(path, interval_ms))


def main(argv=None):
    """Run the viewer; return the exit code (0 on success, 1 on a reported error)."""
    parser = argparse.ArgumentParser(
        prog="python3 -m tools.viz",
        description="Play emulator output (.npy) as a matrix animation.",
    )
    parser.add_argument("path", help=".npy file of shape (frames, rows, cols), +1/-1 or 1/0")
    parser.add_argument("--interval", type=int, default=120, help="milliseconds per frame (default 120)")
    parser.add_argument("--decay", type=float, default=0.6,
                        help="how fast the flip afterglow fades, 0 to below 1 (default 0.6)")
    parser.add_argument("--save", default=None, help="write a .gif or .mp4 instead of opening a window")
    args = parser.parse_args(argv)

    try:
        spins = load_frames(args.path)
        if args.save:
            _make_writer(args.save, args.interval)  # fail fast, before any figure exists
            # Switch before the figure exists so no window opens.
            plt.switch_backend("Agg")
        fig, anim = build_animation(spins, args.interval, args.decay)
        if args.save:
            save_animation(anim, args.save, args.interval)
            plt.close(fig)
        else:
            plt.show()
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
