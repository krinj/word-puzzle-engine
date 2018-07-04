import csv
import os
import sqlite3

from wpg.engine.word import Word


class DataManager:
    def __init__(self):
        pass

    def load_txt(self, file_path, strict=True, min_count=0, max_count=8):

        if not self._check_if_exists(file_path):
            return None

        words = self._extract_words(file_path, strict=strict, min_symbols=min_count, max_symbols=max_count)
        return words

    def load_db(self, file_path):

        if not self._check_if_exists(file_path):
            return None

        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        results = cursor.execute("SELECT * FROM word")
        words = []

        for row in results:
            # Copy the data from the tables.
            literal = row[0]
            verified = bool(row[1])
            hidden = bool(row[2])
            valid = bool(row[3])

            # Create the word object.
            word = Word(literal)
            word.verified = verified
            word.hidden = hidden
            word.valid = valid
            words.append(word)

        # self.sort_words()
        conn.commit()
        conn.close()
        return words

    @staticmethod
    def save(words, file_path, write_unverified=False):

        # All Words.
        text_path = file_path + "_all_words"
        if os.path.exists(text_path):
            os.remove(text_path)
        text_file = open(text_path, "w+")

        # Hidden Words.
        hidden_path = file_path + "_hidden_words"
        if os.path.exists(hidden_path):
            os.remove(hidden_path)
        hidden_file = open(hidden_path, "w+")

        # Valid Words.
        valid_path = file_path + "_valid_words"
        if os.path.exists(valid_path):
            os.remove(valid_path)
        valid_file = open(valid_path, "w+")

        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS word")
        cursor.execute("CREATE TABLE word (key TEXT PRIMARY KEY, verified INT, hidden INT, valid INT)")

        for word in words:

            literal = word.literal
            verified = word.verified
            hidden = word.hidden
            valid = word.valid

            query = "SELECT EXISTS(SELECT 1 FROM word WHERE key='{}' LIMIT 1)".format(literal)
            exists = cursor.execute(query).fetchone()[0]
            if exists == 0:
                query = "INSERT INTO word (key, verified, hidden, valid) VALUES ('{}', {}, {}, {})" \
                    .format(literal, int(verified), int(hidden), int(valid))
                cursor.execute(query)

                if word.valid and (word.verified or write_unverified):
                    text_file.write(literal + "\n")

                if word.valid and (word.hidden or word.suppressed):
                    hidden_file.write(literal + "\n")

                if word.valid and not word.hidden and not word.suppressed:
                    valid_file.write(literal + "\n")

        conn.commit()
        conn.close()

    @staticmethod
    def _check_if_exists(file_path):
        if not os.path.exists(file_path):
            print("Error: File '{}' not found, or could not be opened.".format(file_path))
            files = os.listdir("./")
            if len(files) > 0:
                print
                print("Files in this directory:")
                for file_name in files:
                    print(file_name)
            return False
        return True

    def _extract_words(self, file_path, delimiter='\t', strict=True, min_symbols=0, max_symbols=8):

        word_file = open(file_path, "r")
        words = []

        for line in word_file:

            units = line.split(delimiter)

            # Eliminate proper nouns, or any words with non-alphabet characters.
            if strict and not self._is_valid(units):
                continue

            # Strip away the crap.
            literal = self._strip(units[0], ['\n', '\r', '\t', '.', '"', "'", "-", "&"])

            # Check if the length of the word is within range
            if len(literal) > max_symbols or len(literal) < min_symbols:
                continue

            word = Word(literal.lower())
            words.append(word)

        return words

    @staticmethod
    def _is_valid(literal):
        """ Check to see if this word is valid, from a strict grading point of view. """
        ban_list = ['.', '"', "'", "-", "&"]
        for i in ban_list:
            if i in literal:
                return False

        if literal[0].isupper():
            return False

        return True

    @staticmethod
    def _strip(string, char):
        for c in char:
            string = string.replace(c, "")
        return string

    @staticmethod
    def read_csv(path):
        if not os.path.exists(path):
            raise Exception("File not found: {}".format(path))

        literals = []
        with open(path) as f:
            reader = csv.reader(f)
            for row in reader:
                literal = DataManager._strip(row[0], ['\n', '\r', '\t', '.', '"', "'", "-", "&"])
                literals.append(literal)

        return literals
