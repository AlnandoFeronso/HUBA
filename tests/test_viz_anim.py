import matplotlib

matplotlib.use("Agg")

import gc
import unittest
import warnings
from unittest import mock

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from matplotlib.backend_bases import KeyEvent
from matplotlib.colors import to_rgba

from tools.viz.anim import build_animation, build_figure
from tools.viz.frames import BACKGROUND, GLOW, frame_colors


def setUpModule():
    # Animations built here are never drawn, which matplotlib warns about.
    context = warnings.catch_warnings()
    context.__enter__()
    unittest.addModuleCleanup(context.__exit__, None, None, None)
    unittest.addModuleCleanup(gc.collect)  # runs first: collect while the filter is on
    warnings.filterwarnings("ignore", message="Animation was deleted")


def make_spins():
    """(4, 3, 5): cell [0, 0] flips at frame 1, cell [1, 2] flips at frame 3."""
    s = np.ones((4, 3, 5), dtype=np.int8)
    s[1:, 0, 0] = -1
    s[3, 1, 2] = -1
    return s


def press(fig, key):
    fig.canvas.callbacks.process("key_press_event", KeyEvent("key_press_event", fig.canvas, key))


class BuildFigureTests(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_figure_is_dark_bare_and_shows_frame_zero(self):
        spins = make_spins()
        fig, _ = build_figure(spins)
        self.assertTrue(np.allclose(fig.get_facecolor(), to_rgba(BACKGROUND)))
        self.assertEqual(len(fig.axes), 1)
        self.assertFalse(fig.axes[0].axison)
        images = fig.axes[0].images
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0].get_array().shape, (3, 5, 3))
        self.assertTrue(np.allclose(images[0].get_array(), frame_colors(spins)[0]))
        self.assertEqual(fig.texts[0].get_text(), "0 / 3")

    def test_update_shows_the_requested_frame(self):
        spins = make_spins()
        fig, update = build_figure(spins)
        image = fig.axes[0].images[0]
        update(2)
        self.assertTrue(np.allclose(image.get_array(), frame_colors(spins)[2]))
        self.assertEqual(fig.texts[0].get_text(), "2 / 3")
        update(1)
        self.assertTrue(np.allclose(image.get_array()[0, 0], GLOW))

    def test_gap_lines_only_when_the_longest_side_is_at_most_80(self):
        fig, _ = build_figure(make_spins())
        self.assertEqual(len(fig.axes[0].collections), 2)
        fig, _ = build_figure(np.ones((2, 1, 100), dtype=np.int8))
        self.assertEqual(len(fig.axes[0].collections), 0)

    def test_pixel_size_is_even(self):
        for rows, cols in ((3, 5), (11, 40), (13, 7), (9, 90)):
            with self.subTest(rows=rows, cols=cols):
                fig, _ = build_figure(np.ones((2, rows, cols), dtype=np.int8))
                w, h = fig.get_size_inches() * fig.dpi
                self.assertEqual(int(w) % 2, 0)
                self.assertEqual(int(h) % 2, 0)
                plt.close(fig)


class BuildAnimationTests(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_returns_a_func_animation_with_the_interval(self):
        fig, anim = build_animation(make_spins())
        self.assertIsInstance(anim, animation.FuncAnimation)
        self.assertEqual(anim.event_source.interval, 120)
        _, anim = build_animation(make_spins(), interval_ms=50)
        self.assertEqual(anim.event_source.interval, 50)

    def test_q_and_escape_close_the_figure(self):
        for key in ("q", "escape"):
            with self.subTest(key=key):
                fig, anim = build_animation(make_spins())
                press(fig, key)
                self.assertFalse(plt.fignum_exists(fig.number))

    def test_space_pauses_then_resumes(self):
        fig, anim = build_animation(make_spins())
        with mock.patch.object(anim, "pause") as pause, mock.patch.object(anim, "resume") as resume:
            press(fig, " ")
            pause.assert_called_once()
            resume.assert_not_called()
            press(fig, " ")
            resume.assert_called_once()

    def test_non_positive_interval_is_an_error(self):
        for bad in (0, -5):
            with self.subTest(interval_ms=bad):
                with self.assertRaises(ValueError):
                    build_animation(make_spins(), interval_ms=bad)


if __name__ == "__main__":
    unittest.main()
