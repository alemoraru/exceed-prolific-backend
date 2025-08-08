import unittest
from snippetD import cosine, fixed_vectors, most_similar_pair


class TestSnippetD(unittest.TestCase):
    def test_cosine_similarity(self):
        # Identical vectors
        a = [1, 2, 3]
        b = [1, 2, 3]
        self.assertAlmostEqual(cosine(a, b), 1.0, places=5)
        # Orthogonal vectors
        a = [1, 0, 0]
        b = [0, 1, 0]
        self.assertAlmostEqual(cosine(a, b), 0.0, places=5)
        # Opposite vectors
        a = [1, 0, 0]
        b = [-1, 0, 0]
        self.assertAlmostEqual(cosine(a, b), -1.0, places=5)

    def test_fixed_vectors(self):
        vectors = fixed_vectors()
        self.assertEqual(len(vectors), 4)
        self.assertTrue(all(isinstance(v, list) for v in vectors))

    def test_most_similar_pair(self):
        vectors = fixed_vectors()
        pair = most_similar_pair(vectors)
        self.assertIsInstance(pair, tuple)
        self.assertEqual(len(pair), 2)
        # Check that returned indices are valid
        self.assertTrue(0 <= pair[0] < len(vectors))
        self.assertTrue(0 <= pair[1] < len(vectors))
        # Check that the pair is the most similar
        max_sim = cosine(vectors[pair[0]], vectors[pair[1]])
        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                sim = cosine(vectors[i], vectors[j])
                self.assertTrue(max_sim >= sim or (i, j) == pair)
