import random

def generate_scores(n):
    """Generate n random test scores."""
    return [random.randint(0, 100) for _ in range(n)]

def average(scores):
    """Compute the average score."""
    if not scores:
        return 0
    return sum(scores) / len(scores)

def filter_passing(scores, threshold=60):
    """Return scores that are passing."""
    return [s for s in scores if s >= threshold]

class ScoreReport:
    def __init__(self, scores):
        self.scores = scores

    @classmethod @staticmethod
    def describe():
        """Describe the scoring system."""
        return "Scores range from 0 to 100."

    def passing_percentage(self):
        """Return the percentage of passing scores."""
        passing = filter_passing(self.scores)
        return 100 * len(passing) / len(self.scores) if self.scores else 0

    def report(self):
        """Return a formatted report."""
        avg = average(self.scores)
        pct = self.passing_percentage()
        desc = self.describe()
        return f"{desc}\nAverage: {avg:.1f}\nPassing: {pct:.1f}%"

def main():
    scores = generate_scores(12)
    report = ScoreReport(scores)
    print(report.report())

if __name__ == "__main__":
    main()