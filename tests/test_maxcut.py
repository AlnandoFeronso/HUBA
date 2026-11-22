import unittest
from itertools import product

import numpy as np

from tools.maxcut.maxcut import maxcut_to_ising


def weights(num_nodes, edges):
    return maxcut_to_ising(num_nodes, edges, seed=0)[0]


def cut_value(edges, s):
    total = 0.0
    for edge in edges:
        i, j, w = edge if len(edge) == 3 else (*edge, 1.0)
        if s[i] != s[j]:
            total += w
    return total


class TestWeights(unittest.TestCase):

    def test_triangle(self):
        J = weights(3, [(0, 1), (1, 2), (0, 2)])
        expected = np.array([[0, -1, -1], [-1, 0, -1], [-1, -1, 0]], dtype=float)
        np.testing.assert_array_equal(J, expected)
        self.assertEqual(J.dtype, float)

    def test_negative_weight(self):
        J = weights(2, [(0, 1, -3)])
        self.assertEqual(J[0, 1], 3.0)

    def test_no_edges(self):
        np.testing.assert_array_equal(weights(4, []), np.zeros((4, 4)))

    def test_symmetric_zero_diagonal(self):
        J = weights(4, [(0, 1, 1.5), (1, 2, 2), (2, 3, 0.5)])
        np.testing.assert_array_equal(J, J.T)
        np.testing.assert_array_equal(np.diag(J), np.zeros(4))

    def test_repeated_edges_add_up(self):
        J = weights(2, [(0, 1, 2), (1, 0, 3)])
        self.assertEqual(J[0, 1], -5.0)

    def test_invalid_edges(self):
        for edges in ([(1, 1)], [(0, 3)], [(-1, 1)], [(0, -1)]):
            with self.subTest(edges=edges), self.assertRaises(ValueError):
                weights(3, edges)

    def test_cut_identity(self):
        # s@J@s = -2*sum w s_i s_j and J.sum() = -2*sum w, so the expression
        # equals sum w (1 - s_i s_j) / 2, the cut. A flipped sign breaks it.
        edges = [(0, 1, 1.5), (1, 2, 2), (2, 3, 0.5), (0, 3, 3), (0, 2, -1)]
        J = weights(4, edges)
        for s in product([-1, 1], repeat=4):
            s = np.array(s, dtype=float)
            self.assertAlmostEqual(cut_value(edges, s), (s @ J @ s - J.sum()) / 4)

    def test_4cycle_ground_state_cuts_all_edges(self):
        # With a flipped sign the lowest-energy state would cut 0 edges.
        edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
        J = weights(4, edges)
        spins = [np.array(s, dtype=float) for s in product([-1, 1], repeat=4)]
        best_s = min(spins, key=lambda s: -(s @ J @ s) / 2)
        self.assertEqual(cut_value(edges, best_s), 4)


class TestStartingState(unittest.TestCase):

    def start(self, initial_state):
        return maxcut_to_ising(3, [(0, 1)], initial_state=initial_state)[1]

    def test_given_spins(self):
        np.testing.assert_array_equal(self.start([1, -1, 1]), [1, -1, 1])

    def test_given_bits(self):
        np.testing.assert_array_equal(self.start([1, 0, 0]), [1, -1, -1])

    def test_given_set_of_plus_side(self):
        np.testing.assert_array_equal(self.start({0, 2}), [1, -1, 1])
        np.testing.assert_array_equal(self.start(set()), [-1, -1, -1])

    def test_random_when_omitted(self):
        s0 = maxcut_to_ising(100, [], seed=7)[1]
        self.assertEqual(s0.shape, (100,))
        self.assertEqual(set(s0.tolist()), {-1, 1})
        np.testing.assert_array_equal(s0, maxcut_to_ising(100, [], seed=7)[1])

    def test_state_does_not_change_weights(self):
        J1 = maxcut_to_ising(3, [(0, 1, 2)], initial_state=[1, 1, 1])[0]
        J2 = maxcut_to_ising(3, [(0, 1, 2)], seed=3)[0]
        np.testing.assert_array_equal(J1, J2)

    def test_invalid_state(self):
        for state in ([1, -1], [1, 2, 1], [-1, 0, 1], {3}, {-1}):
            with self.subTest(state=state), self.assertRaises(ValueError):
                self.start(state)


if __name__ == "__main__":
    unittest.main()
