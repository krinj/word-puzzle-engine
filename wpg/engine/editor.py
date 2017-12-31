from wpg.engine.word import Word
from wpg.interface.color import Color


class Editor:
    def __init__(self):
        pass

    def add(self, words, literals=None):
        for literal in literals:
            self.add_single(words, literal.lower())

    @staticmethod
    def add_single(words, literal):
        for word in words:
            if word.literal == literal:
                word.verified = True
                print("Verified: {}".format(literal))
                return
        print("Added: {}".format(literal))
        word = Word(literal)
        word.verified = True
        words.append(word)

    def remove(self, words, literals=None):
        for literal in literals:
            self.remove_single(words, literal.lower())

    @staticmethod
    def remove_single(words, literal):
        for i in range(len(words)):
            word = words[i]
            if word.literal == literal:
                words.pop(i)
                print("Removed: {}".format(literal))
                return
        print("Not Found: {}".format(literal))

    def run_verify(self, words):
        print
        print("Word Verification: Please enter one of the following codes for each word shown.")
        print
        print("y: Yes. The word is valid and should be included.")
        print("n: No. The word is invalid and should be removed.")
        print("x: Exit. Return to the main menu.")

        while True:

            print
            word = None
            word_index = 0

            for i in range(len(words)):
                w = words[i]
                if not w.verified:
                    word = w
                    word_index = i
                    break

            if word is None:
                # All words verified.
                print("Congratulations! All words have been verified.")
                _ = raw_input("Press Enter to Continue.")
                break

            code = raw_input("\t{}: ".format(Color.set_yellow(word.literal)))
            if code == "y":
                word.verified = True
                print("\t{} verified. {} left.".format(word.literal, self._unverified_word_count(words)))

            elif code == "n":
                words.pop(word_index)
                print("\t{} removed. {} left.".format(word.literal, self._unverified_word_count(words)))

            elif code == "x":
                break

            else:
                print("\tInvalid Input. Usage: [y/n/x]")

    @staticmethod
    def _unverified_word_count(words):
        return sum(w.verified is False for w in words)
