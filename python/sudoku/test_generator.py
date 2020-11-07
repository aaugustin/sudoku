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
                solutions = solve(grid)
                self.assertEqual(len(solutions), 1)
