class UserProfile:
    def __init__(self, profile):
        """Initializes the user profile data from input."""
        self.profile = profile

    def display_timeout(self):
        """Displays the user's session timeout setting."""
        print("Timeout is set to:", self.profile['timeout'])


def main():
    user_data_alice = {
        'name': 'Alice',
        'email': 'alice@example.com',
        'age': 30
    }
    user = UserProfile(user_data_alice)
    user.display_timeout()

    user_data_bob = {
        'name': 'Bob',
        'email': '',
        'age': 25,
        'timeout': 300
    }
    user_bob = UserProfile(user_data_bob)
    user_bob.display_timeout()


main()