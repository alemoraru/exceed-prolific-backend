import unittest
from snippetD import ScoringSystem


class TestSnippetD(unittest.TestCase):
    """Unit tests for the ScoringSystem class in snippetD.py."""

    def test_calc_score(self):
        self.assertEqual(ScoringSystem.calc_score(10, 20), 0.4 * 10 + 0.6 * 20)

    def test_calc_score_types(self):
        self.assertIsInstance(ScoringSystem.calc_score(1, 2), float)

    def test_calc_score_zero(self):
        self.assertEqual(ScoringSystem.calc_score(0, 0), 0.0)

    def test_calc_score_negative(self):
        self.assertEqual(ScoringSystem.calc_score(-10, -20), 0.4 * -10 + 0.6 * -20)

    def test_calc_score_large_numbers(self):
        self.assertAlmostEqual(ScoringSystem.calc_score(1e6, 2e6), 0.4 * 1e6 + 0.6 * 2e6)

    def test_calc_score_non_numeric(self):
        with self.assertRaises(TypeError):
            ScoringSystem.calc_score('a', 'b')
