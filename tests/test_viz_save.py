import matplotlib

matplotlib.use("Agg")

import contextlib
import gc
import importlib.util
import io
import os
import tempfile
import unittest
import warnings
from unittest import mock

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation

from tools.viz.anim import build_animation
from tools.viz.cli import main, save_animation
from tools.viz.frames import load_frames

HAS_PIL = importlib.util.find_spec("PIL") is not None


def setUpModule():
    # Animations built here are never drawn, which matplotlib warns about.
    context = warnings.catch_warnings()
    context.__enter__()
    unittest.addModuleCleanup(context.__exit__, None, None, None)
    unittest.addModuleCleanup(gc.collect)  # runs first: collect while the filter is on
    warnings.filterwarnings("ignore", message="Animation was deleted")


def write_run(directory, frames=5):
    """Save a (frames, 3, 6) run where every frame differs from the previous one."""
    a = np.ones((frames, 3, 6), dtype=np.int8)
    for t in range(frames):
        a[t, t % 3, t] = -1
    path = os.path.join(directory, "run.npy")
    np.save(path, a)
    return path


class SaveAnimationTests(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def make_anim(self, directory):
        _, anim = build_animation(load_frames(write_run(directory)))
        return anim

    @unittest.skipUnless(HAS_PIL, "Pillow missing")
    def test_gif_has_one_image_per_frame(self):
        import PIL.Image

        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "out.gif")
            save_animation(self.make_anim(d), path, 50)
            self.assertTrue(os.path.exists(path))
            with PIL.Image.open(path) as gif:
                self.assertEqual(gif.n_frames, 5)

    def test_unknown_extension_is_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError) as ctx:
                save_animation(self.make_anim(d), "out.avi", 50)
            self.assertIn(".gif", str(ctx.exception))

    def test_mp4_without_ffmpeg_names_ffmpeg(self):
        with tempfile.TemporaryDirectory() as d:
            anim = self.make_anim(d)
            with mock.patch.object(animation.FFMpegWriter, "isAvailable", return_value=False):
                with self.assertRaisesRegex(RuntimeError, "ffmpeg"):
                    save_animation(anim, "out.mp4", 50)

    @unittest.skipUnless(animation.FFMpegWriter.isAvailable(), "ffmpeg missing")
    def test_mp4_is_written_when_ffmpeg_exists(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "out.mp4")
            save_animation(self.make_anim(d), path, 50)
            self.assertGreater(os.path.getsize(path), 0)

    def test_zero_interval_is_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                save_animation(self.make_anim(d), "out.gif", 0)


class MainTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(plt, "show")
        self.show = patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        plt.close("all")

    def run_main(self, argv):
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            code = main(argv)
        return code, buf.getvalue()

    def test_plays_in_a_window_without_save(self):
        with tempfile.TemporaryDirectory() as d:
            code, _ = self.run_main([write_run(d)])
        self.assertEqual(code, 0)
        self.show.assert_called_once()

    @unittest.skipUnless(HAS_PIL, "Pillow missing")
    def test_save_writes_the_file_and_opens_no_window(self):
        with tempfile.TemporaryDirectory() as d:
            gif = os.path.join(d, "out.gif")
            code, _ = self.run_main([write_run(d), "--save", gif, "--interval", "50"])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(gif))
        self.show.assert_not_called()

    def test_missing_file_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            code, err = self.run_main([os.path.join(d, "missing.npy")])
        self.assertEqual(code, 1)
        self.assertIn("error:", err)

    def test_wrong_shape_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            bad = os.path.join(d, "bad.npy")
            np.save(bad, np.ones(5))
            code, err = self.run_main([bad])
        self.assertEqual(code, 1)
        self.assertIn("shape", err)

    def test_bad_values_are_reported(self):
        with tempfile.TemporaryDirectory() as d:
            bad = os.path.join(d, "bad.npy")
            np.save(bad, np.full((2, 2, 2), 3))
            code, err = self.run_main([bad])
        self.assertEqual(code, 1)
        self.assertIn("error:", err)

    def test_invalid_argument_exits_through_argparse(self):
        with tempfile.TemporaryDirectory() as d:
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    main([write_run(d), "--interval", "abc"])

    def test_bad_save_extension_is_reported_before_any_window(self):
        with tempfile.TemporaryDirectory() as d:
            code, err = self.run_main([write_run(d), "--save", os.path.join(d, "out.avi")])
        self.assertEqual(code, 1)
        self.assertIn(".gif", err)
        self.show.assert_not_called()


if __name__ == "__main__":
    unittest.main()
