import unittest
from snippetB import UserData, summarize_scores


class TestSnippetB(unittest.TestCase):
    def test_scores_are_stored(self):
        user = UserData("Alice", [10, 30, 60])
        self.assertEqual(user.scores, [10, 30, 60])

    def test_top_score(self):
        user = UserData("Bob", [5, 15, 80])
        self.assertEqual(user.top_score(), 80)

    def test_top_score_empty(self):
        user = UserData("Dave", [])
        self.assertEqual(user.top_score(), 0)

    def test_top_score_negative(self):
        user = UserData("Frank", [-10, -20, -5])
        self.assertEqual(user.top_score(), -5)

    def test_top_score_single(self):
        user = UserData("Eve", [42])
        self.assertEqual(user.top_score(), 42)

    def test_top_score_mixed(self):
        user = UserData("Grace", [10, -5, 20])
        self.assertEqual(user.top_score(), 20)

    def test_add_score(self):
        user = UserData("Carol", [20, 30])
        self.assertEqual(user.top_score(), 30)
        user.add_score(50)
        self.assertEqual(user.scores, [20, 30, 50])
        self.assertEqual(user.top_score(), 50)

    def test_add_score_empty(self):
        user = UserData("Hank", [])
        user.add_score(100)
        self.assertEqual(user.scores, [100])
        self.assertEqual(user.top_score(), 100)

    def test_add_score_negative(self):
        user = UserData("Ivy", [10, 20])
        self.assertEqual(user.top_score(), 20)
        user.add_score(-10)
        self.assertEqual(user.scores, [10, 20, -10])
        self.assertEqual(user.top_score(), 20)

    def test_add_duplicate_score(self):
        user = UserData("Jack", [10, 20])
        self.assertEqual(user.top_score(), 20)
        user.add_score(20)
        self.assertEqual(user.scores, [10, 20, 20])
        self.assertEqual(user.top_score(), 20)

    def test_add_zero_score(self):
        user = UserData("Kate", [])
        self.assertEqual(user.top_score(), 0)
        user.add_score(0)
        self.assertEqual(user.scores, [0])
        self.assertEqual(user.top_score(), 0)

    def test_summarize_scores(self):
        users = [UserData("A", [10, 90]), UserData("B", [50, 50])]
        summary = summarize_scores(users)
        self.assertEqual(summary["A"], 90)
        self.assertEqual(summary["B"], 50)
