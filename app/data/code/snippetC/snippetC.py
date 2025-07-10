class ScoreTracker:
    def __init__(self):
        """Initializes with a list of recent test scores."""
        self.scores = [85, 90, 88, 92]

    def print_last_score(self):
        """Prints the last score in the list."""
        print("Last score:", self.scores[len(self.scores)])


def main():
    tracker = ScoreTracker()
    tracker.print_last_score()


main()
