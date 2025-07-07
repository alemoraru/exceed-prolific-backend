import unittest
from snippetA import SalesProcessor
from snippetB import UserProfile
from snippetC import ScoreTracker
from snippetD import ScoringSystem


class TestSnippetA(unittest.TestCase):
    def test_total_sales_type_error(self):
        processor = SalesProcessor()
        # The error is triggered because sales_data contains strings, not ints
        with self.assertRaises(TypeError):
            processor.total_sales()

    def test_sales_data_is_list_of_str(self):
        processor = SalesProcessor()
        self.assertTrue(all(isinstance(x, str) for x in processor.sales_data))

    def test_total_sales_initial_value(self):
        processor = SalesProcessor()
        self.assertEqual(processor.sales_data[0], '100')


class TestSnippetB(unittest.TestCase):
    def test_missing_timeout_key(self):
        # Profile without 'timeout' key should raise KeyError
        user_data = {'name': 'Alice', 'email': 'alice@example.com', 'age': 30}
        user = UserProfile(user_data)
        with self.assertRaises(KeyError):
            user.display_timeout()

    def test_with_timeout_key(self):
        user_data = {'name': 'Bob', 'email': '', 'age': 25, 'timeout': 300}
        user = UserProfile(user_data)
        # Should not raise
        user.display_timeout()

    def test_profile_has_name(self):
        user_data = {'name': 'Alice', 'email': 'alice@example.com', 'age': 30}
        user = UserProfile(user_data)
        self.assertIn('name', user.profile)

    def test_profile_age_type(self):
        user_data = {'name': 'Bob', 'email': '', 'age': 25, 'timeout': 300}
        user = UserProfile(user_data)
        self.assertIsInstance(user.profile['age'], int)


class TestSnippetC(unittest.TestCase):
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


class TestSnippetD(unittest.TestCase):
    def test_attribute_error(self):
        system = ScoringSystem()
        # The error is triggered because calculate_score is not defined
        with self.assertRaises(NameError):
            system.process_scores(50, 70)

    def test_calc_score(self):
        self.assertEqual(ScoringSystem.calc_score(10, 20), 0.4 * 10 + 0.6 * 20)

    def test_calc_score_types(self):
        self.assertIsInstance(ScoringSystem.calc_score(1, 2), float)
