"""Matplotlib figure and looping animation for the matrix viewer."""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation

from tools.viz.frames import BACKGROUND, TEXT, frame_colors


def build_figure(spins, decay=0.6):
    """Return (fig, update): a dark, bare figure showing the matrix, and update(i) to show frame i."""
    n, rows, cols = spins.shape
    colors = frame_colors(spins, decay)

    # Pixel sizes are even because ffmpeg needs that for MP4. The extra 0.01 stops
    # float rounding from losing a pixel when matplotlib truncates inches * dpi.
    w_px = max(300, min(1200, 30 * cols + 80))
    h_px = max(150, min(800, 30 * rows + 80))
    with plt.rc_context({"toolbar": "none"}):
        fig = plt.figure(figsize=((w_px + 0.01) / 100, (h_px + 0.01) / 100), dpi=100, facecolor=BACKGROUND)

    ax = fig.add_axes([0.03, 0.12, 0.94, 0.85], facecolor=BACKGROUND)
    ax.set_axis_off()
    im = ax.imshow(colors[0], interpolation="nearest", aspect="equal")
    if max(rows, cols) <= 80:
        ax.hlines(np.arange(-0.5, rows, 1.0), -0.5, cols - 0.5, colors=BACKGROUND, linewidth=1.5)
        ax.vlines(np.arange(-0.5, cols, 1.0), -0.5, rows - 0.5, colors=BACKGROUND, linewidth=1.5)
    counter = fig.text(0.5, 0.04, f"0 / {n - 1}", color=TEXT, fontsize=8, ha="center", va="center")

    def update(i):
        im.set_data(colors[i])
        counter.set_text(f"{i} / {n - 1}")
        return [im, counter]

    return fig, update


def build_animation(spins, interval_ms=120, decay=0.6):
    """Return (fig, anim): a looping animation. It never calls plt.show.

    q or escape closes the figure; space pauses and resumes. The caller must keep a
    reference to anim, or the animation stops.
    """
    if interval_ms <= 0:
        raise ValueError("interval_ms must be positive")

    fig, update = build_figure(spins, decay)
    anim = animation.FuncAnimation(fig, update, frames=len(spins), interval=interval_ms, repeat=True, blit=False)
    paused = {"on": False}

    def on_key(event):
        if event.key == " ":
            if paused["on"]:
                anim.resume()
            else:
                anim.pause()
            paused["on"] = not paused["on"]
        elif event.key in ("q", "escape"):
            plt.close(fig)

    fig.canvas.mpl_connect("key_press_event", on_key)
    return fig, anim
