import numpy as np


def maxcut_to_ising(num_nodes, edges, initial_state=None, seed=None):
    """Return (J, s0): the coupling matrix and starting spins for a Max-Cut graph.

    Edges are (i, j) or (i, j, weight) with nodes 0..num_nodes-1; default weight 1.
    initial_state is one value per node (+1/-1 or 1/0) or a set of the nodes on
    the +1 side. Without it, s0 is random; pass seed to make it repeatable.
    """
    J = np.zeros((num_nodes, num_nodes), dtype=float)

    for edge in edges:
        if len(edge) == 2:
            i, j = edge
            weight = 1.0
        else:
            i, j, weight = edge

        if i == j:
            raise ValueError(f"Self-loop on node {i}")
        # Explicit range check: a negative index would otherwise wrap around.
        if not (0 <= i < num_nodes and 0 <= j < num_nodes):
            raise ValueError(f"Node index out of range: ({i}, {j}) for {num_nodes} nodes")

        # The machine minimises E = -sum J_ij s_i s_j, so J_ij = -w_ij makes
        # low energy mean a large cut. -= also makes repeated edges add up.
        J[i, j] -= weight
        J[j, i] -= weight

    if initial_state is None:
        s0 = np.random.default_rng(seed).choice([-1, 1], size=num_nodes)
    elif isinstance(initial_state, (set, frozenset)):
        if not all(0 <= i < num_nodes for i in initial_state):
            raise ValueError(f"initial_state has a node outside 0..{num_nodes - 1}")
        s0 = np.full(num_nodes, -1)
        s0[list(initial_state)] = 1
    else:
        s0 = np.asarray(initial_state)
        if s0.shape != (num_nodes,):
            raise ValueError(f"initial_state needs one value per node ({num_nodes})")
        values = set(s0.tolist())
        if not (values <= {-1, 1} or values <= {0, 1}):
            raise ValueError("initial_state values must be all +1/-1 or all 1/0")
        s0 = np.where(s0 > 0, 1, -1)

    return J, s0
