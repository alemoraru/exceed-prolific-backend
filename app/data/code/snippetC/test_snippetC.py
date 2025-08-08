import unittest
from snippetC import generate_scores, average, filter_passing, ScoreReport


class TestSnippetC(unittest.TestCase):
    def test_generate_scores(self):
        scores = generate_scores(5)
        self.assertEqual(len(scores), 5)
        for s in scores:
            self.assertTrue(0 <= s <= 100)

    def test_generate_scores_edge_cases(self):
        self.assertEqual(generate_scores(0), [])
        scores = generate_scores(1)
        self.assertEqual(len(scores), 1)
        self.assertTrue(0 <= scores[0] <= 100)

    def test_average(self):
        self.assertEqual(average([10, 20, 30]), 20)
        self.assertEqual(average([]), 0)

    def test_average_negative_and_float(self):
        self.assertEqual(average([-10, 10]), 0)
        self.assertAlmostEqual(average([1.5, 2.5, 3.5]), 2.5)

    def test_filter_passing(self):
        scores = [55, 60, 75, 40]
        passing = filter_passing(scores)
        self.assertEqual(passing, [60, 75])
        self.assertEqual(filter_passing(scores, threshold=70), [75])

    def test_filter_passing_all_failing(self):
        scores = [10, 20, 30]
        self.assertEqual(filter_passing(scores), [])

    def test_filter_passing_all_passing(self):
        scores = [60, 70, 80]
        self.assertEqual(filter_passing(scores), scores)

    def test_filter_passing_custom_threshold(self):
        scores = [55, 60, 75, 40]
        self.assertEqual(filter_passing(scores, threshold=75), [75])
        self.assertEqual(filter_passing(scores, threshold=100), [])

    def test_score_report(self):
        scores = [50, 60, 70, 80]
        report = ScoreReport(scores)
        self.assertEqual(report.passing_percentage(), 75.0)
        self.assertIn("Scores range from 0 to 100.", report.report())
        self.assertIn("Average: 65.0", report.report())
        self.assertIn("Passing: 75.0%", report.report())

    def test_score_report_empty_scores(self):
        report = ScoreReport([])
        self.assertEqual(report.passing_percentage(), 0)
        self.assertIn("Scores range from 0 to 100.", report.report())
        self.assertIn("Average: 0.0", report.report())
        self.assertIn("Passing: 0.0%", report.report())

    def test_score_report_all_passing(self):
        scores = [100, 90, 80]
        report = ScoreReport(scores)
        self.assertEqual(report.passing_percentage(), 100.0)
        self.assertIn("Passing: 100.0%", report.report())

    def test_score_report_all_failing(self):
        scores = [10, 20, 30]
        report = ScoreReport(scores)
        self.assertEqual(report.passing_percentage(), 0.0)
        self.assertIn("Passing: 0.0%", report.report())

    def test_score_negative_threshold(self):
        scores = [50, 60, 70, 80]
        report = ScoreReport(scores)
        self.assertEqual(filter_passing(scores, threshold=-10), scores)
        # For passing, the default threshold is 60 always, so the 50 score should not be counted
        self.assertIn("Passing: 75.0%", report.report())

    def test_score_report_describe(self):
        self.assertEqual(ScoreReport.describe(), "Scores range from 0 to 100.")

    def test_score_report_report_format(self):
        scores = [60, 70]
        report = ScoreReport(scores)
        output = report.report()
        self.assertTrue(output.startswith("Scores range from 0 to 100."))
        self.assertIn("Average: 65.0", output)
        self.assertIn("Passing: 100.0%", output)
