import os
import sqlite3

from wpg.engine.word import Word


class DataManager:
    def __init__(self):
        pass

    def load_txt(self, file_path, max_count=7):

        if not self._check_if_exists(file_path):
            return None

        words = self._extract_words(file_path, max_symbols=max_count)
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

            # Create the word object.
            word = Word(literal)
            word.verified = verified
            words.append(word)

        # self.sort_words()
        conn.commit()
        conn.close()
        return words

    @staticmethod
    def save(words, file_path):
        text_path = file_path + "_text"
        if os.path.exists(text_path):
            os.remove(text_path)
        text_file = open(text_path, "w+")

        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS word")
        cursor.execute("CREATE TABLE word (key TEXT PRIMARY KEY, verified INT)")

        for word in words:
            literal = word.literal
            verified = word.verified
            query = "SELECT EXISTS(SELECT 1 FROM word WHERE key='{}' LIMIT 1)".format(literal)
            exists = cursor.execute(query).fetchone()[0]
            if exists == 0:
                query = "INSERT INTO word (key, verified) VALUES ('{}', {})" \
                    .format(literal, int(verified))
                cursor.execute(query)
                text_file.write(literal + "\n")

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

    def _extract_words(self, file_path, delimiter='\t', max_symbols=8):

        word_file = open(file_path, "r")
        words = []

        for line in word_file:

            units = line.split(delimiter)
            literal = self._strip(units[0], ['\n', '\r', '\t', '.', '"', "'", "-", "&"])

            if len(literal) > max_symbols:
                continue

            word = Word(literal.lower())
            words.append(word)

        return words

    @staticmethod
    def _strip(string, char):
        for c in char:
            string = string.replace(c, "")
        return string
