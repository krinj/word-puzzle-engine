import sqlite3

from wpg.utils import util
from wpg.word import Word


class Importer:
    def __init__(self):
        pass

    def create_db(self, db_path, words):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS word")
        cursor.execute("CREATE TABLE word (key TEXT PRIMARY KEY, score INT)")

        for word in words:
            literal = word.literal
            score = word.score
            query = "SELECT EXISTS(SELECT 1 FROM word WHERE key='{}' LIMIT 1)".format(literal)
            exists = cursor.execute(query).fetchone()[0]
            if exists == 0:
                query = "INSERT INTO word (key, score) VALUES ('{}', {})".format(literal, score)
                cursor.execute(query)

        conn.commit()
        conn.close()

    def _get_words(self, db_path):
        words = []
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        results = cursor.execute("SELECT * FROM word")
        for row in results:
            word = Word(row[0], 1, row[1])
            words.append(word)

        conn.close()
        return words

    def extract_literals(self, file_path):
        words = self.extract_words(file_path, divide=1)
        return [word.literal for word in words]

    def extract_words(self, file_path, ban_list=None, db_path=None, delimiter='\t', max_symbols=8, divide=1, max_words=0):
        word_file = open(file_path, "r")
        i = 0
        words = []
        ban_count = 0
        for line in word_file:
            units = line.split(delimiter)
            score = 0

            if len(units) > 1:
                score = int(util.strip(units[1], ['\n', '\r', '\t', '.']))

            literal = util.strip(units[0], ['\n', '\r', '\t', '.'])

            if ban_list is not None and literal in ban_list:
                ban_count += 1
                continue

            if divide > 0:
                word_array = util.divide_string(literal, divide)

            if len(word_array) > max_symbols:
                continue

            word = Word(literal, divide, score)
            words.append(word)
            i += 1
            if max_words != 0 and i > max_words:
                break

        if db_path is not None:
            self.create_db(db_path, words)

        if ban_count > 0:
            print("Words Banned: {}".format(ban_count))
        return words
