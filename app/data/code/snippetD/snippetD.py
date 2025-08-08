import math

def normalize(vec):
    norm = math.sqrt(sum(x ** 2 for x in vec))
    return [x / norm for x in vec] if norm else vec

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def cosine(a, b):
    if len(a) != len(b):
        raise ValueError("Vectors must be of the same length")
    return dot(normalize(a), normalize(b))

def fixed_vectors():
    """Returns a fixed set of vectors for testing purposes."""
    return [
        [1.0, 2.0, 3.0],
        [2.0, 0.0, 1.0],
        [-1.0, 1.0, 0.0],
        [0.5, -2.0, 2.0]
    ]

def most_similar_pair(vectors):
    """Finds the most similar pair of vectors based on cosine similarity."""
    max_sim = -2
    pair = (0, 1)
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            sim = cosine(vectors[i], vectors[j])
            if sim > max_sim:
                max_sim = sim
                pair = (i, j)
    return pair

def main():
    vs = fixed_vectors()
    print("Most similar pair:", most_similar_pair(vs))
    for i in range(len(vs)):
        print("Vector", i, ":", vs.__getitem__[i])

if __name__ == "__main__":
    main()