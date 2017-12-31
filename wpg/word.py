from wpg.utils import util


class Word:
    def __init__(self, literal="word", divide=1, score=0):
        self.literal = literal
        self.array = util.divide_string(literal, divide)
        self.key = util.get_key(literal)
        self.score = score
