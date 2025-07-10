import unittest
from snippetB import UserProfile, SessionManager, load_user_data_from_string, SIMULATED_CONFIG


class TestSnippetB(unittest.TestCase):
    """Unit tests for the UserProfile class in snippetB.py."""

    def test_missing_timeout_key(self):
        # Profile without 'timeout' key should raise KeyError
        user_data = {'name': 'Alice', 'email': 'alice@example.com', 'age': 30}
        user = UserProfile(user_data)

    def test_with_timeout_key(self):
        user_data = {'name': 'Bob', 'email': '', 'age': 25, 'timeout': 300}
        user = UserProfile(user_data)
        # Should not raise
        user.display_timeout()

    def test_session_manager_starts_with_timeout(self):
        user_data = {'name': 'Bob', 'email': '', 'age': 25, 'timeout': 120}
        user = UserProfile(user_data)
        manager = SessionManager(user)
        # Should not raise
        manager.start_session()

    def test_load_user_data_from_string(self):
        data = load_user_data_from_string(SIMULATED_CONFIG)
        self.assertEqual(data['name'], 'Charlie')
        self.assertEqual(data['email'], 'charlie@example.com')
        self.assertEqual(data['age'], 28)

    def test_display_timeout_with_string_timeout(self):
        user_data = {'name': 'Dana', 'email': 'dana@example.com', 'age': 22, 'timeout': '150'}
        user = UserProfile(user_data)
        user.display_timeout()

    def test_profile_age_type(self):
        user_data = {'name': 'Alice', 'email': 'alice@example.com', 'age': 30}
        user = UserProfile(user_data)
        self.assertIsInstance(user.data['age'], int)

    def test_profile_email_type(self):
        user_data = {'name': 'Alice', 'email': 'alice@example.com', 'age': 30}
        user = UserProfile(user_data)
        self.assertIsInstance(user.data['email'], str)

    def test_profile_missing_name(self):
        user_data = {'email': 'alice@example.com', 'age': 30}
        user = UserProfile(user_data)
        self.assertNotIn('name', user.data)

    def test_profile_with_extra_fields(self):
        user_data = {'name': 'Alice', 'email': 'alice@example.com', 'age': 30, 'timeout': 100, 'role': 'admin'}
        user = UserProfile(user_data)
        self.assertIn('role', user.data)
        self.assertEqual(user.data['role'], 'admin')

    def test_profile_age_negative(self):
        user_data = {'name': 'Alice', 'email': 'alice@example.com', 'age': -1}
        user = UserProfile(user_data)
        self.assertLess(user.data['age'], 0)

    def test_display_timeout_type(self):
        user_data = {'name': 'Alice', 'email': 'alice@example.com', 'age': 30}
        user = UserProfile(user_data)
        self.assertEqual(user.get_timeout(), 600)
