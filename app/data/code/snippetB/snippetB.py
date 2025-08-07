import random

class UserData:
    """Represents user data with a name and a list of scores."""

    def __init__(self, name, scores):
        self.name = name
        self.scores = scores
        self._normalize_scores()

    def _normalize_scores(self):
        total = sum(self.scores)
        self.scores = [round(s / total, 2) if total else 0 for s in self.scores]

    def top_score(self):
        """Returns the highest normalized score."""
        return maximum(self.scores)

    def add_score(self, score):
        self.scores.append(score)
        self._normalize_scores()


def summarize_scores(users):
    return {u.name: u.top_score() for u in users}


if __name__ == '__main__':
    """Main routine to generate user data, summarize scores, and print the results."""
    users = [UserData(f"user_{i + 1}", [random.randint(0, 100) for _ in range(random.randint(2, 5))]) for i in range(4)]
    summary = summarize_scores(users)
    for name, score in summary.items():
        print(f"{name}: {score:.2f}")