import csv

from wpg.data.data_manager import DataManager
from wpg.engine.word import Word
from wpg.interface.color import Color


class Editor:
    def __init__(self):
        pass

    def add(self, words, literals=None):
        for literal in literals:
            if ".csv" in literal:
                sub_literals = DataManager.read_csv(literal)
                self.add(words, sub_literals)
            else:
                self.add_single(words, literal.lower())

    @staticmethod
    def add_single(words, literal):
        target_word = None

        for word in words:
            if word.literal == literal:
                target_word = word
                break

        if target_word is None:
            target_word = Word(literal)
            words.append(target_word)

        target_word.verified = True
        target_word.valid = True
        target_word.hidden = False
        print("Added: {}".format(literal))

    def hide(self, words, literals=None):
        for literal in literals:
            if ".csv" in literal:
                sub_literals = DataManager.read_csv(literal)
                self.hide(words, sub_literals)
            else:
                self.hide_single(words, literal.lower())

    @staticmethod
    def hide_single(words, literal):

        # Look for the target word.
        target_word = None
        for word in words:
            if word.literal == literal:
                target_word = word
                break

        # Word was not found, so add it.
        if target_word is None:
            target_word = Word(literal)
            words.append(target_word)

        # Toggle between hiding or showing the word.
        target_word.verified = True
        target_word.valid = True
        target_word.hidden = not target_word.hidden
        if target_word.hidden:
            print("Hide: {}".format(literal))
        else:
            print("Show: {}".format(literal))

    def remove(self, words, literals=None):
        for literal in literals:
            if ".csv" in literal:
                sub_literals = DataManager.read_csv(literal)
                self.remove(words, sub_literals)
            else:
                self.remove_single(words, literal.lower())

    @staticmethod
    def remove_single(words, literal):
        for i in range(len(words)):
            word = words[i]
            if word.literal == literal:
                word.valid = False
                word.verified = True
                print("Removed: {}".format(literal))
                return
        print("Not Found: {}".format(literal))

    def run_batch_verify(self, words):
        print
        print("Batch Verification: Please the index of a word to verify it, or one of the following commands.")
        print
        print("<i>: The word at this index will be verified. The rest will be hidden.")
        print("h: All words on this list will be hidden.")
        print("x: Exit. Return to the main menu.")

        while True:

            print

            unverified_words = []
            for i in range(len(words)):
                w = words[i]
                if not w.verified:
                    unverified_words.append(w)

            if len(unverified_words) == 0:
                # All words verified.
                print("Congratulations! All words have been verified.")
                _ = raw_input("Press Enter to Continue.")
                break

            # Decide the batch of words.
            batch_words = []
            while len(batch_words) < 10 and len(unverified_words) > 0:
                batch_words.append(unverified_words.pop(0))

            # Show all the words.
            for i in range(len(batch_words)):
                print("{}. {}".format(i, batch_words[i].literal))

            # Accept the input
            print("")
            code = raw_input("\t{}: ".format(Color.set_yellow("Input")))
            index = -1

            try:
                index = int(code)
            except:
                pass

            if index != -1 and index < len(batch_words):
                # Verify the indexed word.
                self._hide_words(batch_words)
                word = batch_words[index]
                word.verified = True
                word.verified = True
                word.valid = True
                word.hidden = False
                print("\t{} verified. {} left.".format(word.literal, self._unverified_word_count(words)))

            elif code == "h":
                self._hide_words(batch_words)
                print("\tWords hidden. {} left.".format(self._unverified_word_count(words)))

            elif code == "x":
                break

            else:
                print("\tInvalid Input. Usage: [y/n/x]")

    def _hide_words(self, words):
        for word in words:
            word.verified = True
            word.valid = True
            word.hidden = True

    def run_verify(self, words):

        print
        print("Word Verification: Please enter one of the following codes for each word shown.")
        print
        print("y: Yes. The word is valid and should be included.")
        print("n: No. The word is invalid and should be removed.")
        print("h: Hide. The word is valid, but should be marked as hidden.")
        print("x: Exit. Return to the main menu.")

        while True:

            print
            word = None

            for i in range(len(words)):
                w = words[i]
                if not w.verified:
                    word = w
                    break

            if word is None:
                # All words verified.
                print("Congratulations! All words have been verified.")
                _ = raw_input("Press Enter to Continue.")
                break

            code = raw_input("\t{}: ".format(Color.set_yellow(word.literal)))
            if code == "y":
                word.verified = True
                word.valid = True
                word.hidden = False
                print("\t{} verified. {} left.".format(word.literal, self._unverified_word_count(words)))

            elif code == "n":
                word.valid = False
                word.verified = True
                print("\t{} removed. {} left.".format(word.literal, self._unverified_word_count(words)))

            elif code == "h":
                word.verified = True
                word.valid = True
                word.hidden = True
                print("\t{} hidden. {} left.".format(word.literal, self._unverified_word_count(words)))

            elif code == "x":
                break

            else:
                print("\tInvalid Input. Usage: [y/n/x]")

    @staticmethod
    def _unverified_word_count(words):
        return sum(w.verified is False for w in words)
