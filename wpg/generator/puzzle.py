class Puzzle:
    def __init__(self, key, words, score, collision_score, generator_score):
        self.key = key
        self.words = words
        self.score = score
        self.collision_score = collision_score
        self.generator_score = generator_score
