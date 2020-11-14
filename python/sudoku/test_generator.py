import random
import unittest

from .generator import generate
from .solver import solve


class TestGenerate(unittest.TestCase):
    def test_generate(self):
        for seed in range(5):
            with self.subTest(seed=42 << seed):
                random.seed(seed)
                grid = generate()

                # Most grids have between 55 and 60 zeroes
                zero_count = list(grid).count(0)
                self.assertGreaterEqual(zero_count, 50)
                self.assertLessEqual(zero_count, 65)

                solutions = solve(grid)
                self.assertEqual(len(solutions), 1)
