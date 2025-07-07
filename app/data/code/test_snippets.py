import unittest
from snippetA import build_list
from snippetB import top_three
from snippetC import get_third_element
from snippetD import parse_numbers


class TestSnippetA(unittest.TestCase):
    """Test cases for the snippetA module."""

    def test_0(self):
        self.assertEqual(build_list(0), [])

    def test_1(self):
        self.assertEqual(build_list(1), [0])

    def test_3(self):
        self.assertEqual(build_list(3), [0, 1, 2])

    def test_4(self):
        self.assertEqual(build_list(4), [0, 1, 2, 3])

    def test_5(self):
        self.assertEqual(build_list(5), list(range(5)))

    def test_negative_5(self):
        self.assertEqual(build_list(-5), list(range(-5)))


class TestSnippetB(unittest.TestCase):
    """Test cases for the snippetB module."""

    def test_1(self):
        self.assertEqual(top_three([1, 2]), [2, 1])

    def test_2(self):
        self.assertEqual(top_three([5, 1, 3, 4, 2]), [5, 4, 3])

    def test_3(self):
        self.assertEqual(top_three([10, 9, 8, 7]), [10, 9, 8])


class TestSnippetC(unittest.TestCase):
    """Test cases for the snippetC module."""

    def test_1(self):
        self.assertEqual(get_third_element([1, 2, 3]), 3)

    def test_2(self):
        self.assertEqual(get_third_element(["a", "b", "c", "d"]), "c")


class TestSnippetD(unittest.TestCase):
    """Test cases for the snippetD module."""

    def test_1(self):
        self.assertEqual(parse_numbers("1,2,3"), [1, 2, 3])

    def test_2(self):
        self.assertEqual(parse_numbers("10"), [10])

    def test_3(self):
        self.assertEqual(parse_numbers(""), [])
