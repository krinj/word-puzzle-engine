import os
import sqlite3


class MetaWord:
    def __init__(self, literal):
        self.literal = literal
        self.verified = False
        self.rare = False


class Color:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    END = '\033[0m'

    def __init__(self):
        pass

    @staticmethod
    def set_yellow(string):
        return Color.YELLOW + string + Color.END

    @staticmethod
    def set_green(string):
        return Color.GREEN + string + Color.END

    @staticmethod
    def set_blue(string):
        return Color.BLUE + string + Color.END


class Action:
    def __init__(self, name, keys, desc_text, usage_text, delegate, has_args=False):
        self.name = name
        self.keys = keys
        self.desc_text = desc_text
        self.usage_text = usage_text
        self.delegate = delegate
        self.has_args = has_args

    def print_description(self):
        print(Color.set_yellow(self.usage_text))
        print(self.desc_text)
        if len(self.keys) > 1:
            print("Hotkey: {}".format(self.keys[1:]))
        print


def clear_terminal():
    os.system("clear || cls")


def enter_to_continue():
    print
    raw_input(Color.set_green("Press <ENTER> to continue."))


class WordSorter:
    def __init__(self, db_path):

        self.db_path = db_path
        self.words = []
        self.show_instructions = True

        C_ADD = Action(name="Add New Word",
                       keys=["add"],
                       desc_text="Adds (and verifies) the specified word to the dictionary.",
                       usage_text="add [word]",
                       delegate=self.add,
                       has_args=True)

        C_REMOVE = Action(name="Remove Word",
                          keys=["remove"],
                          desc_text="Removes the specified word from the dictionary.",
                          usage_text="remove [word]",
                          delegate=self.remove,
                          has_args=True)

        C_INFO = Action(name="Information",
                        keys=["info"],
                        desc_text="Displays the stats and information for this dictionary.",
                        usage_text="info",
                        delegate=self.show_info)

        C_VERIFY = Action(name="Verify",
                          keys=["verify"],
                          desc_text="Comb through the dictionary and manually verify words.",
                          usage_text="verify",
                          delegate=self.run_verify)

        C_SAVE = Action(name="Save",
                        keys=["save"],
                        desc_text="Save the changes made to this collection.",
                        usage_text="save",
                        delegate=self.save)

        C_EXIT = Action(name="Exit",
                        keys=["exit"],
                        desc_text="Save and exit the app.",
                        usage_text="exit",
                        delegate=self.exit_app)

        self.actions = [C_ADD,
                        C_REMOVE,
                        C_VERIFY,
                        C_INFO,
                        C_SAVE,
                        C_EXIT]

    def print_status(self):
        word_count = len(self.words)
        verified_count = sum(w.verified is True for w in self.words)
        unverified_count = word_count - verified_count
        print
        print("Number of Words: {}".format(word_count))
        print("Verified Words: {}".format(verified_count))
        print("Unverified Words: {}".format(unverified_count))
        print

    def load_text(self, file_path, max_count):
        self.words = self._extract_words(file_path, max_symbols=max_count)
        print("Loading from '{}'".format(file_path))

    def unverified_word_count(self):
        return sum(w.verified is False for w in self.words)

    def sort_words(self):
        self.words.sort(key=lambda w: w.literal)

    # -------------------------------------------------------------------------------

    # Actions

    def add(self, literals=None):
        for literal in literals:
            self.add_single(literal.lower())
        self.sort_words()

    def add_single(self, literal):
        for word in self.words:
            if word.literal == literal:
                word.verified = True
                print("Verified: {}".format(literal))
                return
        print("Added: {}".format(literal))
        word = MetaWord(literal)
        self.words.append(word)

    def remove(self, literals=None):
        for literal in literals:
            self.remove_single(literal.lower())
        self.sort_words()

    def remove_single(self, literal):
        for i in range(len(self.words)):
            word = self.words[i]
            if word.literal == literal:
                self.words.pop(i)
                print("Removed: {}".format(literal))
                return
        print("Not Found: {}".format(literal))

    def show_info(self):

        self.print_status()
        self.sort_words()

        w_count = 0
        # print("First 25 words:")
        for word in self.words:
            print(word.literal)
            w_count += 1
            if w_count > 25:
                break

    def run_verify(self):
        clear_terminal()
        print
        print("Word Verification: Please enter one of the following codes for each word shown.")
        print
        print("y: Yes. The word is valid and should be included.")
        print("n: No. The word is invalid and should be removed.")
        print("r: Rare. The word is valid, but it is not a common word")
        print("x: Exit. Return to the main menu.")

        while True:

            print
            word = None
            word_index = 0

            for i in range(len(self.words)):
                w = self.words[i]
                if not w.verified:
                    word = w
                    word_index = i
                    break

            if word is None:
                # All words verified.
                print("Congratulations! All words have been verified.")
                enter_to_continue()
                break

            code = raw_input("\t{}: ".format(Color.set_yellow(word.literal)))
            if code == "y":
                word.verified = True
                print("\t{} verified. {} left.".format(word.literal, self.unverified_word_count()))

            elif code == "n":
                self.words.pop(word_index)
                print("\t{} removed. {} left.".format(word.literal, self.unverified_word_count()))

            elif code == "r":
                word.verified = True
                word.rare = True
                print("\t{} verified as rare. {} left.".format(word.literal, self.unverified_word_count()))

            elif code == "x":
                self.show_instructions = True
                break

            else:
                print("\tInvalid Input. Usage: [y/n/r/x]")

    def save(self):
        self.save_db()
        print("Collection saved.")

    def exit_app(self):
        self.save()
        exit(1)

    # -------------------------------------------------------------------------------

    # Run Process Loop

    def run(self):
        while True:
            self.run_select_mode()

    def run_select_mode(self):

        print
        if self.show_instructions:
            clear_terminal()
            print("Please specify your action.")
            print
            for action in self.actions:
                action.print_description()
            self.show_instructions = False

        code = raw_input(Color.set_green("Enter Command: "))
        print

        code_array = code.split(" ")
        code_key = code_array[0]
        code_args = None
        if len(code_array) > 1:
            code_args = code_array[1:]

        action_found = False
        for action in self.actions:
            if code_key in action.keys:
                # Valid action found.
                action_found = True
                if action.has_args:
                    if code_args is None:
                        print("You must supply some input arguments.")
                        print(action.usage_text)
                    else:
                        action.delegate(code_args)
                else:
                    action.delegate()

        # No action found
        if not action_found:
            print("Invalid action. Command not recognized.")

    # -------------------------------------------------------------------------------

    # Data Organization

    def save_db(self):

        text_path = self.db_path + "_text"
        if os.path.exists(text_path):
            os.remove(text_path)
        text_file = open(text_path, "w+")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS word")
        cursor.execute("CREATE TABLE word (key TEXT PRIMARY KEY, verified INT, rare INT)")

        for word in self.words:
            literal = word.literal
            verified = word.verified
            rare = word.rare
            query = "SELECT EXISTS(SELECT 1 FROM word WHERE key='{}' LIMIT 1)".format(literal)
            exists = cursor.execute(query).fetchone()[0]
            if exists == 0:
                query = "INSERT INTO word (key, verified, rare) VALUES ('{}', {}, {})"\
                    .format(literal, int(verified), int(rare))
                cursor.execute(query)
                if int(rare) == 0:
                    text_file.write(literal + "\n")

        conn.commit()
        conn.close()

    def load_db(self):

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        results = cursor.execute("SELECT * FROM word")
        self.words = []

        for row in results:
            literal = row[0]
            verified = bool(row[1])
            rare = bool(row[2])
            word = MetaWord(literal)
            word.verified = verified
            word.rare = rare
            self.words.append(word)

        self.sort_words()
        conn.commit()
        conn.close()

    # --------------------------------------------------------------------------------

    # String Utils.

    def _extract_words(self, file_path, delimiter='\t', max_symbols=8):

        word_file = open(file_path, "r")
        words = []

        for line in word_file:

            units = line.split(delimiter)
            literal = self._strip(units[0], ['\n', '\r', '\t', '.', '"', "'", "-", "&"])

            if len(literal) > max_symbols:
                continue

            word = MetaWord(literal.lower())
            words.append(word)

        return words

    def _strip(self, string, char):
        for c in char:
            string = string.replace(c, "")
        return string
