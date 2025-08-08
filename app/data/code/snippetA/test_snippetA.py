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
