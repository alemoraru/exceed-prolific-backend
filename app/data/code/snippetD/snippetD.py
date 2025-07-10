class ScoringSystem:

    @staticmethod
    def calc_score(x, y):
        """Returns a weighted score based on two inputs."""
        return 0.4 * x + 0.6 * y

    def process_scores(self, x, y):
        """Processes and prints a score using a helper function."""
        score = calculate_score(x, y)
        print("Final score:", score)


def main():
    system = ScoringSystem()
    system.process_scores(50, 70)


main()
