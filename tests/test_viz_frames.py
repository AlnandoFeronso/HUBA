import os
import pathlib
import tempfile
import unittest

import numpy as np

from tools.viz.frames import load_frames, glow_levels, frame_colors, PLUS, MINUS, GLOW


def make_a():
    """(3, 2, 4) of +1 with two -1 cells."""
    a = np.ones((3, 2, 4), dtype=int)
    a[1, 0, 1] = -1
    a[2, 1, 3] = -1
    return a


def make_s():
    """(4, 1, 2): column 0 is +1, -1, -1, -1 over the frames; column 1 is always +1."""
    s = np.ones((4, 1, 2), dtype=np.int8)
    s[1:, 0, 0] = -1
    return s


class TestLoadFrames(unittest.TestCase):
    def test_3d_array_keeps_shape_and_becomes_int8(self):
        a = make_a()
        result = load_frames(a)
        self.assertEqual(result.shape, (3, 2, 4))
        self.assertEqual(result.dtype, np.int8)
        self.assertTrue(np.array_equal(result, a))

    def test_all_ones_is_accepted(self):
        result = load_frames(np.ones((2, 3, 4), dtype=int))
        self.assertEqual(result.shape, (2, 3, 4))
        self.assertTrue((result == 1).all())

    def test_zero_one_input_maps_zero_to_minus_one(self):
        result = load_frames([[[1, 0]]])
        self.assertTrue(np.array_equal(result, np.array([[[1, -1]]])))

    def test_2d_input_becomes_one_row_per_frame(self):
        self.assertEqual(load_frames(np.ones((4, 6), dtype=int)).shape, (4, 1, 6))

    def test_loads_from_str_and_path(self):
        a = make_a()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "run.npy")
            np.save(path, a)
            self.assertTrue(np.array_equal(load_frames(path), a))
            self.assertTrue(np.array_equal(load_frames(pathlib.Path(path)), a))

    def test_input_is_not_modified(self):
        a = np.array([[[1, 0], [0, 1]]])
        before = a.copy()
        load_frames(a)
        self.assertTrue(np.array_equal(a, before))

    def test_wrong_number_of_dimensions_mentions_the_shape(self):
        for bad in (np.ones(5), np.ones((1, 2, 3, 4))):
            with self.subTest(shape=bad.shape):
                with self.assertRaisesRegex(ValueError, "shape"):
                    load_frames(bad)

    def test_empty_input_is_an_error(self):
        for bad in (np.zeros((0, 2, 2)), np.zeros((3, 0))):
            with self.subTest(shape=bad.shape):
                with self.assertRaises(ValueError):
                    load_frames(bad)

    def test_bad_values_are_an_error(self):
        bad_inputs = {
            "two": np.full((1, 2, 2), 2),
            "half": np.full((1, 2, 2), 0.5),
            "minus_zero_plus": np.array([[[-1, 0, 1]]]),
            "minus_zero": np.array([[[-1, 0]]]),
        }
        for name, bad in bad_inputs.items():
            with self.subTest(case=name):
                with self.assertRaises(ValueError):
                    load_frames(bad)


class TestGlow(unittest.TestCase):
    def test_glow_fades_after_a_flip(self):
        glow = glow_levels(make_s(), 0.6)
        np.testing.assert_allclose(glow[:, 0, 0], [0, 1, 0.6, 0.36])
        np.testing.assert_allclose(glow[:, 0, 1], 0)

    def test_a_new_flip_restarts_at_one(self):
        s = np.ones((4, 1, 2), dtype=np.int8)
        s[1, 0, 0] = -1  # column 0: +1, -1, +1, +1
        np.testing.assert_allclose(glow_levels(s, 0.6)[:, 0, 0], [0, 1, 1, 0.6])

    def test_zero_decay_glows_only_on_the_flip_frame(self):
        np.testing.assert_allclose(glow_levels(make_s(), 0)[:, 0, 0], [0, 1, 0, 0])

    def test_single_frame_has_no_glow(self):
        glow = glow_levels(np.ones((1, 2, 3), dtype=np.int8))
        self.assertEqual(glow.shape, (1, 2, 3))
        self.assertTrue((glow == 0).all())

    def test_decay_outside_range_is_an_error(self):
        for bad in (-0.1, 1.0):
            with self.subTest(decay=bad):
                with self.assertRaises(ValueError):
                    glow_levels(make_s(), bad)


class TestColors(unittest.TestCase):
    def make_c(self):
        c = np.ones((4, 1, 2), dtype=np.int8)
        c[:, 0, 1] = -1  # column 1 is always -1
        c[1:, 0, 0] = -1  # column 0: +1, -1, -1, -1
        return c

    def test_shape_and_range(self):
        colors = frame_colors(self.make_c())
        self.assertEqual(colors.shape, (4, 1, 2, 3))
        self.assertTrue(((colors >= 0) & (colors <= 1)).all())

    def test_base_colours_and_glow_blend(self):
        colors = frame_colors(self.make_c())
        self.assertTrue(np.allclose(colors[0, 0, 0], PLUS))
        self.assertTrue(np.allclose(colors[0, 0, 1], MINUS))
        self.assertTrue(np.allclose(colors[1, 0, 0], GLOW))
        expected = 0.4 * np.array(MINUS) + 0.6 * np.array(GLOW)
        self.assertTrue(np.allclose(colors[2, 0, 0], expected))

    def test_zero_decay_returns_to_the_base_colour(self):
        colors = frame_colors(self.make_c(), 0)
        self.assertTrue(np.allclose(colors[2, 0, 0], MINUS))


if __name__ == "__main__":
    unittest.main()
