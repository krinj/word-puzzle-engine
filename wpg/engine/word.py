from wpg.utils import util


class Word:
    def __init__(self, literal):
        self.literal = literal
        self.verified = False
        self.key = util.get_key(literal)
