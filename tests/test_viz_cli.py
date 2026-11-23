"""Integration tests: run the real command `python3 -m tools.viz` in a subprocess."""
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest

import numpy as np

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HAS_PIL = importlib.util.find_spec("PIL") is not None


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "tools.viz", *args],
        cwd=SRC_ROOT,
        env={**os.environ, "MPLBACKEND": "Agg"},
        capture_output=True,
        text=True,
        timeout=90,
    )


def write_run(directory, frames=5):
    """Save a (frames, 3, 6) run where every frame differs from the previous one."""
    a = np.ones((frames, 3, 6), dtype=np.int8)
    for t in range(frames):
        a[t, t % 3, t] = -1
    path = os.path.join(directory, "run.npy")
    np.save(path, a)
    return path


class CommandLineTests(unittest.TestCase):
    @unittest.skipUnless(HAS_PIL, "Pillow missing")
    def test_save_gif_has_one_image_per_frame(self):
        import PIL.Image

        with tempfile.TemporaryDirectory() as d:
            gif = os.path.join(d, "out.gif")
            result = run_cli(write_run(d), "--save", gif, "--interval", "50")
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            with PIL.Image.open(gif) as image:
                self.assertEqual(image.n_frames, 5)

    def test_invalid_npy_exits_with_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            bad = os.path.join(d, "bad.npy")
            np.save(bad, np.ones(5))
            result = run_cli(bad, "--save", os.path.join(d, "out.gif"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("error:", result.stderr)

    def test_missing_file_exits_with_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            result = run_cli(os.path.join(d, "missing.npy"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("error:", result.stderr)


if __name__ == "__main__":
    unittest.main()
