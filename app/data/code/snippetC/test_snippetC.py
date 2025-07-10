import unittest

from snippetC import ScoreTracker


class TestSnippetC(unittest.TestCase):
    """Unit tests for the ScoreTracker class in snippetC.py."""

    def test_index_error(self):
        tracker = ScoreTracker()
        # The error is triggered because len(self.scores) is out of bounds
        with self.assertRaises(IndexError):
            tracker.print_last_score()

    def test_scores_length(self):
        tracker = ScoreTracker()
        self.assertEqual(len(tracker.scores), 4)

    def test_scores_are_ints(self):
        tracker = ScoreTracker()
        self.assertTrue(all(isinstance(x, int) for x in tracker.scores))

    def test_print_last_score_valid(self):
        tracker = ScoreTracker()
        tracker.scores = [10, 20, 30, 40]
        # Should print 40, but we just check no exception is raised
        try:
            tracker.print_last_score()
        except Exception as e:
            self.fail(f"print_last_score() raised {type(e)} unexpectedly!")

    def test_scores_with_negative_values(self):
        tracker = ScoreTracker()
        tracker.scores = [-5, -10, -15, -20]
        self.assertTrue(all(x < 0 for x in tracker.scores))

    def test_scores_with_mixed_types(self):
        tracker = ScoreTracker()
        tracker.scores = [10, "20", 30, 40]
        with self.assertRaises(Exception):
            tracker.print_last_score()

    def test_empty_scores(self):
        tracker = ScoreTracker()
        tracker.scores = []
        with self.assertRaises(IndexError):
            tracker.print_last_score()
