from wpg.utils import util


class Word:
    def __init__(self, literal):
        self.literal = literal
        self.verified = False  # If this word has been checked by a human.
        self.hidden = False  # If this word should be hidden off the list.
        self.valid = False  # If this word is valid to be used. We keep a list of fake words for better merging.
        self.suppressed = False  # A word can be valid - but if it is suppressed it acts as if it is hidden.
        self.key = util.get_key(literal)

    @property
    def playable(self):
        return self.verified and self.valid and not self.hidden and not self.suppressed
