import sqlite3

from wpg.data.symbol import Symbol, SymbolString


class Importer:
    def __init__(self):
        self.symbols = []
        self.symbol_strings = []
        pass

    def create_db(self, db_path, symbol_strings):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS symbol_string")
        cursor.execute("CREATE TABLE symbol_string (key VARCHAR PRIMARY KEY, score INT)")

        for symbol_string in symbol_strings:
            query = "SELECT EXISTS(SELECT 1 FROM symbol_string WHERE key='{}' LIMIT 1)".format(symbol_string.literal)
            exists = cursor.execute(query).fetchone()[0]
            if exists == 0:
                query = "INSERT INTO symbol_string (key, score) VALUES ('{}', {})".format(symbol_string.literal, 0)
                cursor.execute(query)

        conn.commit()
        conn.close()

    # def set_symbols(self, file_path):
    #     print("Setting Symbols")
    #     word_file = open(file_path, "r")
    #     self.symbols = []
    #     for line in word_file:
    #         word = Importer.strip(line, ['\n', '\r', '\t', '.'])
    #         symbol = Symbol(word)
    #         self.symbols.append(symbol)
    #
    #     for s in self.symbols:
    #         print("ID: {}, VALUE: {}, REP: {}".format(s.id, s.value, s.get_rep()))
    #


    def extract_words(self, file_path, max_symbols=8, divide=1, max_words=5):
        word_file = open(file_path, "r")
        i = 0
        symbol_strings = []
        for line in word_file:
            literal = Importer.strip(line, ['\n', '\r', '\t', '.'])
            if divide > 0:
                word = Importer.divide_string(literal, divide)
            if len(word) > max_symbols:
                continue

            sym_str = SymbolString(literal, word)
            symbol_strings.append(sym_str)
            i += 1
            if max_words != 0 and i > max_words:
                break

        for sym_str in symbol_strings:
            print(sym_str.literal)
            print(sym_str.array)
            print("")

        return symbol_strings

    @staticmethod
    def divide_string(string, n=3):
        # Returns an array of strings, divided by n-length from the original string.
        return [string[i:i + n] for i in range(0, len(string), n)]

    @staticmethod
    def strip(string, char):
        for c in char:
            string = string.replace(c, "")
        return string



        # Use this class to import data from a given text file into a SQLlite format. We will use the SQLlite from here on.
