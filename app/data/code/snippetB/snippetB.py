import json

# Simulated external JSON config
SIMULATED_CONFIG = """
{
    "name": "Charlie",
    "email": "charlie@example.com",
    "age": 28
}
"""


class UserProfile:
    """
    A simple class to represent a user profile with session timeout settings.
    The default session timeout is set to 600 seconds if not specified.
    """

    def __init__(self, data: dict):
        """Wrap raw user data."""
        self.data = data

    def get_timeout(self):
        """Retrieve the session timeout setting (seconds)."""
        return int(self.data["timeout"])

    def display_timeout(self):
        """Display the session timeout setting."""
        timeout = self.get_timeout()
        print(f"Session timeout is set to {timeout} seconds.")


class SessionManager:
    """A class to manage user sessions based on their profile settings."""

    def __init__(self, profile: UserProfile):
        self.profile = profile

    def start_session(self):
        """Start a user session with the configured timeout."""
        timeout = self.profile.get_timeout()
        name = self.profile.data.get("name", "<unknown>")
        print(f"Starting session for {name} (timeout: {timeout}s)")


def load_user_data_from_string(config_str: str) -> dict:
    print("Loading user data from embedded JSON...")
    return json.loads(config_str)


def main():
    user_data = load_user_data_from_string(SIMULATED_CONFIG)
    profile = UserProfile(user_data)
    manager = SessionManager(profile)
    manager.start_session()


if __name__ == "__main__":
    main()
