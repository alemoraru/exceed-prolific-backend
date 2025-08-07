import unittest
from snippetC import generate_scores, average, filter_passing, ScoreReport


class TestSnippetC(unittest.TestCase):
    def test_generate_scores(self):
        scores = generate_scores(5)
        self.assertEqual(len(scores), 5)
        for s in scores:
            self.assertTrue(0 <= s <= 100)

    def test_average(self):
        self.assertEqual(average([10, 20, 30]), 20)
        self.assertEqual(average([]), 0)

    def test_filter_passing(self):
        scores = [55, 60, 75, 40]
        passing = filter_passing(scores)
        self.assertEqual(passing, [60, 75])
        self.assertEqual(filter_passing(scores, threshold=70), [75])

    def test_score_report(self):
        scores = [50, 60, 70, 80]
        report = ScoreReport(scores)
        self.assertEqual(report.passing_percentage(), 75.0)
        self.assertIn('Scores range from 0 to 100.', report.report())
        self.assertIn('Average: 65.0', report.report())
        self.assertIn('Passing: 75.0%', report.report())

    def test_describe(self):
        self.assertEqual(ScoreReport.describe(), 'Scores range from 0 to 100.')
