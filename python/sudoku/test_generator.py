import random
import unittest

from .generator import generate
from .solver import solve


class TestGenerate(unittest.TestCase):
    def test_generate(self):
        for seed in range(5):
            with self.subTest(seed=42 << seed):
                random.seed(seed)
                grid, difficulty = generate()

                # Most grids have difficulty below 6
                self.assertGreaterEqual(difficulty, 1)
                self.assertLessEqual(difficulty, 10)

                # Most grids have between 55 and 60 zeroes
                zero_count = list(grid).count(0)
                self.assertGreaterEqual(zero_count, 50)
                self.assertLessEqual(zero_count, 65)

                solutions, solve_difficulty = solve(grid)
                self.assertEqual(len(solutions), 1)
                self.assertEqual(solve_difficulty, difficulty)
