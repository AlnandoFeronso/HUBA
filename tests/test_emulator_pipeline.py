import os
import random
import tempfile
import unittest

import numpy as np

from tools.emulator.main import Bit, save_frames, snapshot, sweep

try:
    from tools.maxcut.maxcut import maxcut_to_ising
    from tools.viz.frames import load_frames
except ImportError:  # these live on their own branches until merged
    maxcut_to_ising = load_frames = None


def make_grid(rows, cols, s0=None):
    return [[Bit(x, y, value=None if s0 is None else int(s0[x * cols + y]))
             for y in range(cols)] for x in range(rows)]


def run(grid, j, t, steps):
    frames = [snapshot(grid)]
    for _ in range(steps):
        sweep(grid, j, t)
        frames.append(snapshot(grid))
    return frames


class TestJMatrixMatchesNeighbourGrid(unittest.TestCase):
    """A J matrix with j on the four torus neighbours must behave exactly like scalar j."""

    def test_same_frames_for_same_seed(self):
        rows, cols, j, t = 3, 4, 1.0, 2.27
        n = rows * cols
        J = np.zeros((n, n))
        for x in range(rows):
            for y in range(cols):
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    J[x * cols + y, (nx % rows) * cols + ny % cols] = j

        random.seed(1)
        scalar = run(make_grid(rows, cols), j, t, 10)
        random.seed(1)
        matrix = run(make_grid(rows, cols), J, t, 10)
        self.assertEqual(scalar, matrix)


@unittest.skipIf(maxcut_to_ising is None, "needs tools/maxcut and tools/viz merged")
class TestMaxcutToEmulatorToViz(unittest.TestCase):
    # 4-cycle on a 2x2 grid: the best cut puts alternate nodes on one side (cut = 4)
    EDGES = [(0, 1), (1, 2), (2, 3), (3, 0)]
    ROWS, COLS = 2, 2

    def setUp(self):
        self.J, self.s0 = maxcut_to_ising(4, self.EDGES, initial_state={0, 1})
        random.seed(0)
        self.frames = run(make_grid(self.ROWS, self.COLS, self.s0), self.J, 0.1, 30)

    def test_frame_zero_is_the_maxcut_start_state(self):
        self.assertEqual(self.frames[0], [[1, 1], [-1, -1]])

    def test_low_temperature_finds_the_max_cut(self):
        s = np.array(self.frames[-1]).ravel()
        cut = sum(1 for i, j in self.EDGES if s[i] != s[j])
        self.assertEqual(cut, 4)  # a flipped J sign would settle on cut 0

    def test_file_is_read_by_the_viz_loader(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "run.npy")
            save_frames(self.frames, path)
            spins = load_frames(path)
        self.assertEqual(spins.shape, (31, self.ROWS, self.COLS))
        self.assertEqual(spins.dtype, np.int8)
        self.assertEqual(spins.tolist(), self.frames)


if __name__ == "__main__":
    unittest.main()
