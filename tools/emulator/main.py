import math
import random
import sys
import time

import numpy as np


class Bit:
    def __init__(self, x, y, bias = 0.0, value = None):
        self.x = x
        self.y = y
        self.value = random.choice([-1, 1]) if value is None else value
        self.bias = bias

    def calculate_value(self, grid, j = 1.0, t = 1.0):
        def sigmoid(x):
            return 1 / (1 + math.exp(-x))

        rows = len(grid)
        cols = len(grid[0])

        if isinstance(j, np.ndarray):
            # j is the (n, n) matrix from maxcut_to_ising; node k sits at grid[k // cols][k % cols]
            s = j[self.x * cols + self.y] @ [bit.value for row in grid for bit in row] + self.bias
        else:
            neighbors = [
                grid[(self.x - 1) % rows][self.y].value,
                grid[(self.x + 1) % rows][self.y].value,
                grid[self.x][(self.y - 1) % cols].value,
                grid[self.x][(self.y + 1) % cols].value
            ]
            s = sum(neighbors) * j + self.bias

        p = sigmoid(2 * s / t)

        rand = random.uniform(0, 1)
        if rand <= p:
            self.value = 1
        else:
            self.value = -1

def sweep(grid, j, t):
    rows, cols = len(grid), len(grid[0])
    for _ in range(rows * cols):
        grid[random.randint(0, rows - 1)][random.randint(0, cols - 1)].calculate_value(grid, j, t)


def snapshot(grid):
    return [[bit.value for bit in row] for row in grid]


def save_frames(frames, path):
    # (frames, rows, cols) of +1/-1, frame 0 = starting state: what tools/viz reads
    np.save(path, np.array(frames, dtype=np.int8))


if __name__ == '__main__':
    rows = 11
    cols = 40
    max_steps = 100
    step = 0
    j = 1
    t = 2.27

    # todo jakos lepiej zaprogramowac/zaprojektowac ten algorytm dla sensownego problemu (komiwojazer?)
    # model Isinga czy cos takiego, jakies inne modele
    # czy da sie 3d/4d/nd? i czy to ma sens?
    # rozne geometrie sasiadow?
    hello_world_map = [
        "██  ██  ██████  ██      ██      ██████  ",
        "██  ██  ██      ██      ██      ██  ██  ",
        "██████  ████    ██      ██      ██  ██  ",
        "██  ██  ██      ██      ██      ██  ██  ",
        "██  ██  ██████  ██████  ██████  ██████  ",
        "                                        ",
        "█    █  ██████  ██████  ██      █████   ",
        "█    █  ██  ██  ██  ██  ██      ██  ██  ",
        "█ ██ █  ██  ██  ██████  ██      ██   █  ",
        "██  ██  ██  ██  █   █   ██      ██  ██  ",
        "█    █  ██████  █    █  ██████  █████   "
    ]

    # init
    max_bias = 4.0
    min_bias = -4.0
    grid = []
    for x in range(rows):
        row_bits = []
        for y in range(cols):
            char = hello_world_map[x][y] if y < len(hello_world_map[x]) else " "
            pixel_bias = max_bias if char == "█" else min_bias

            row_bits.append(Bit(x, y, bias=pixel_bias))
        grid.append(row_bits)

    frames = [snapshot(grid)]

    print("\033[2J", end="")

    while True:
        step += 1
        sweep(grid, j, t)
        frames.append(snapshot(grid))

        print("\033[H", end="")
        print(f"\n-------------- Step {step} ---------------")
        for row in grid:
            print("".join(["█" if bit.value == 1 else " " for bit in row]))

        if step >= max_steps:
            break

        time.sleep(0.05)

    if len(sys.argv) > 1:
        save_frames(frames, sys.argv[1])
