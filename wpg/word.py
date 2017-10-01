from wpg import util


class Word:
    def __init__(self, value="word", score=0):
        self.value = value
        self.key = util.get_key(value)
        self.score = score
