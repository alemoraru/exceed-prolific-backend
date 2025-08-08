import unittest
import os
from snippetA import BookShelf, add_book, count_books


class TestSnippetA(unittest.TestCase):
    def setUp(self):
        self.log = "test_books.log"
        # Ensure log is clean
        if os.path.exists(self.log):
            os.remove(self.log)

    def tearDown(self):
        if os.path.exists(self.log):
            os.remove(self.log)

    def test_add_and_count_books(self):
        add_book(self.log, "Book One")
        add_book(self.log, "Book Two")
        self.assertEqual(count_books(self.log), 2)

    def test_preview(self):
        add_book(self.log, "Book One")
        add_book(self.log, "Book Two")
        shelf = BookShelf(self.log)
        preview = shelf.preview()
        self.assertIn("Book One", preview)
        self.assertIn("Book Two", preview)

    def test_summary(self):
        add_book(self.log, "Book One")
        shelf = BookShelf(self.log)
        self.assertEqual(shelf.summary(), "Books logged: 1")

    def test_preview_no_log(self):
        shelf = BookShelf("nonexistent.log")
        self.assertEqual(shelf.preview(), "No log found.")

    def test_add_book_empty_title(self):
        add_book(self.log, "")
        self.assertEqual(count_books(self.log), 1)
        shelf = BookShelf(self.log)
        self.assertIn("", shelf.preview())

    def test_add_book_duplicate_titles(self):
        add_book(self.log, "Book X")
        add_book(self.log, "Book X")
        self.assertEqual(count_books(self.log), 2)

    def test_count_books_empty_log(self):
        open(self.log, "w").close()
        self.assertEqual(count_books(self.log), 0)

    def test_preview_more_than_two_books(self):
        add_book(self.log, "Book 1")
        add_book(self.log, "Book 2")
        add_book(self.log, "Book 3")
        shelf = BookShelf(self.log)
        preview = shelf.preview()
        self.assertIn("Book 1", preview)
        self.assertIn("Book 2", preview)
        self.assertNotIn("Book 3", preview)
        self.assertEqual(count_books(self.log), 3)

    def test_summary_no_books(self):
        self.assertEqual(BookShelf(self.log).summary(), "Books logged: 0")

    def test_summary_multiple_books(self):
        for i in range(5):
            add_book(self.log, f"Book {i}")
        self.assertEqual(BookShelf(self.log).summary(), "Books logged: 5")

    def test_add_book_nonexistent_log(self):
        logname = "nonexistent2.log"
        if os.path.exists(logname):
            os.remove(logname)
        add_book(logname, "Book Y")
        self.assertEqual(count_books(logname), 1)

    def test_preview_after_log_deleted(self):
        add_book(self.log, "Book Z")
        os.remove(self.log)
        shelf = BookShelf(self.log)
        self.assertEqual(shelf.preview(), "No log found.")

    def test_add_book_special_characters(self):
        title = "Book!@#$%^&*()_+"
        add_book(self.log, title)
        shelf = BookShelf(self.log)
        self.assertIn(title, shelf.preview())

    def test_preview_malformed_lines(self):
        with open(self.log, "w") as f:
            f.write("Malformed line\nAnother bad line\n")
        shelf = BookShelf(self.log)
        preview = shelf.preview()
        self.assertIn("Malformed line", preview)
        self.assertIn("Another bad line", preview)

    def test_add_and_count_large_number_of_books(self):
        for i in range(100):
            add_book(self.log, f"Book {i}")
        self.assertEqual(count_books(self.log), 100)
