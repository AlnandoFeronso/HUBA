<p align="center"><strong>HUBA</strong> &middot; <em>FPGA-based probabilistic computer</em></p>

---

# Max-Cut to Ising input

> How to turn a Max-Cut graph into the coupling matrix `J` and starting spins `s0` for HUBA, for anyone feeding it a Max-Cut problem.

| Field  | Value                         |
|--------|-------------------------------|
| Status | Draft                         |
| Date   | 2026-11-21                    |
| Author | Emilia Łukasiuk               |

## Purpose

HUBA solves Ising problems, so a Max-Cut graph must first become a coupling matrix and a starting state.

## Details

The machine minimises `E(s) = -Σ_{i<j} J_ij s_i s_j` with spins `s_i ∈ {-1, +1}` marking the side of the cut, so `J_ij = -w_ij` (no bias) makes the lowest energy the largest cut. Repeated edges add up.

`maxcut_to_ising(num_nodes, edges, initial_state=None, seed=None)` returns `(J, s0)`:

- `edges` are `(i, j)` or `(i, j, weight)` with nodes `0..num_nodes-1`; default weight 1, negative weights allowed.
- `initial_state` is one value per node (`+1/-1` or `1/0`) or a set of the nodes on the `+1` side.
- Without `initial_state`, `s0` is random; pass `seed` to make it repeatable.
- Self-loops, out-of-range nodes and a malformed `initial_state` raise `ValueError`. Requires NumPy.

```python
from tools.maxcut.maxcut import maxcut_to_ising

J, s0 = maxcut_to_ising(3, [(0, 1), (1, 2), (0, 2)], initial_state={0})
print(J)
print(s0)
```

```text
[[ 0. -1. -1.]
 [-1.  0. -1.]
 [-1. -1.  0.]]
[ 1 -1 -1]
```

## References

- [1] Same energy convention as `tools/emulator/main.py`

---

<p align="center"><sub><strong>HUBA</strong> &middot; Licensed under the Apache License 2.0 &middot; see the <code>LICENSE</code> file in the repository root</sub></p>
