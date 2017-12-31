from wpg.data.data_manager import DataManager
from wpg.engine.editor import Editor
from wpg.interface.color import Color


class Engine:
    def __init__(self):
        print("Engine Initialized")

        # Logic Modules
        self.data_manager = DataManager()
        self.editor = Editor()
        self.generator = None

        # State Data
        self.db_path = None
        self.words = []

    # ==================================================================================================================
    # Data Manager
    # ==================================================================================================================

    def load_db(self, file_path):
        self.db_path = file_path
        self._set_words(self.data_manager.load_db(self.db_path))

    def save(self):
        if self.db_path is None:
            self.db_path = raw_input(Color.set_green("Enter a name for this database: "))
        self.data_manager.save(self.words, self.db_path)

    def load_txt(self, file_path):
        self.db_path = None
        self._set_words(self.data_manager.load_txt(file_path))
        self.save()

    def print_info(self):
        word_count = len(self.words)
        verified_count = sum(w.verified is True for w in self.words)
        unverified_count = word_count - verified_count
        print
        print("Database Status [{}]:".format(self.db_path))
        print("Number of Words: {}".format(word_count))
        print("Verified Words: {}".format(verified_count))
        print("Unverified Words: {}".format(unverified_count))
        print

    def _set_words(self, words):
        if words is not None:
            self.words = words
            self._sort_words()
            print("Words Loaded {}".format(len(self.words)))

    # ==================================================================================================================
    # Editor
    # ==================================================================================================================

    def add(self, literals):
        self.editor.add(self.words, literals)

    def remove(self, literals):
        self.editor.remove(self.words, literals)

    def verify(self):
        self.editor.run_verify(self.words)

    # ==================================================================================================================
    # Generator
    # ==================================================================================================================

    

    # ==================================================================================================================
    # Utils
    # ==================================================================================================================

    def _sort_words(self):
        self.words.sort(key=lambda w: w.literal)
