import unittest
from snippetB import UserData, summarize_scores


class TestSnippetB(unittest.TestCase):
    def test_scores_are_stored(self):
        user = UserData('Alice', [10, 30, 60])
        self.assertEqual(user.scores, [10, 30, 60])

    def test_top_score(self):
        user = UserData('Bob', [5, 15, 80])
        self.assertEqual(user.top_score(), 80)

    def test_add_score(self):
        user = UserData('Carol', [20, 30])
        self.assertEqual(user.top_score(), 30)
        user.add_score(50)
        self.assertEqual(user.scores, [20, 30, 50])
        self.assertEqual(user.top_score(), 50)

    def test_summarize_scores(self):
        users = [UserData('A', [10, 90]), UserData('B', [50, 50])]
        summary = summarize_scores(users)
        self.assertEqual(summary['A'], 90)
        self.assertEqual(summary['B'], 50)
