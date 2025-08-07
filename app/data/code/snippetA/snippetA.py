import os
from datetime import datetime

class BookShelf:
    def __init__(self, log):
        self.log = log

    def preview(self):
        """
        Shows first two book titles, if any.
        """
        if not os.path.exists(self.log):
            return "No log found."
        with open(self.log) as f:
            lines = f.readlines()
        preview = "".join(lines[:2])
        return f"""Preview:\n{preview}""

    def summary(self):
        """
        Gives a summary of the log.
        """
        total = count_books(self.log)
        return f"Books logged: {total}"

def add_book(log, title):
    """
    Adds a book entry with timestamp.
    """
    with open(log, 'a') as f:
        f.write(f"{datetime.now().isoformat()} - {title}\n")

def count_books(log):
    """
    Counts books in the log.
    """
    if not os.path.exists(log):
        return 0
    with open(log) as f:
        return sum(1 for _ in f)