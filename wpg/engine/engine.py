import csv

from wpg.data.data_manager import DataManager
from wpg.data.file_splitter import FileSplitter
from wpg.engine.editor import Editor
from wpg.generator.block_def import BlockDef
from wpg.generator.generator import Generator
from wpg.interface.color import Color


class Engine:

    K_PUZZLE_BATCH = 25
    K_WRITE_UNVERIFIED = True  # Will write words into the output dict even if it is unverified.

    def __init__(self):

        # Logic Modules
        self.data_manager = DataManager()
        self.editor = Editor()
        self.generator = Generator()
        self.version = 4.1

        # State Data
        self.db_path = None
        self.words = []
        self.words_dirty = True

        # Key Mask
        self.used_keys = {}

    # ==================================================================================================================
    # Data Manager
    # ==================================================================================================================

    def load_used_keys(self, file_path):
        self.used_keys = {}
        with open(file_path, 'rb') as f:
            reader = csv.reader(f, delimiter=' ')
            for row in reader:
                self.used_keys[row[0]] = True

    def load_db(self, file_path):
        self.db_path = file_path
        self._set_words(self.data_manager.load_db(self.db_path))
        self.words_dirty = True
        print("Database Loaded!")

    def save(self):
        if self.db_path is None:
            self.db_path = raw_input(Color.set_green("Enter a name for this database: "))
        self.generator.suffix_suppression(self.words)
        self.data_manager.save(self.words, self.db_path, self.K_WRITE_UNVERIFIED)
        print("Database Saved!")

    def load_txt(self, file_path, strict, min_count, max_count):
        self.db_path = None
        self._set_words(self.data_manager.load_txt(file_path, strict=strict, min_count=min_count, max_count=max_count))
        self.words_dirty = True
        self.save()

    def merge_txt(self, file_path, strict, min_count, max_count):
        loaded_words = self.data_manager.load_txt(file_path, strict=strict, min_count=min_count, max_count=max_count)
        added_words = 0
        for loaded_word in loaded_words:
            if not any(word.literal == loaded_word.literal for word in self.words):
                self.words.append(loaded_word)
                added_words += 1

        self.words_dirty = True
        print("Words Added: {}".format(added_words))

    def split_txt(self, file_path, max_units, min_count, max_count):
        loaded_words = self.data_manager.load_txt(file_path, strict=False, min_count=min_count, max_count=max_count)
        splitter = FileSplitter(file_path, min_count, max_count)
        splitter.process(loaded_words, max_units)
        print("Words Split: {}".format(len(loaded_words)))

    def print_info(self):
        word_count = len(self.words)
        verified_count = sum(w.verified is True for w in self.words)
        valid_count = sum(w.playable is True for w in self.words)
        hidden_count = sum(w.hidden is True for w in self.words)
        unverified_count = word_count - verified_count
        print
        print("Database Status [{}]:".format(self.db_path))
        print("Number of Words: {}".format(word_count))
        print("Playable Words: {}".format(valid_count))
        print("Verified Words: {}".format(verified_count))
        print("Unverified Words: {}".format(unverified_count))
        print("Hidden Words: {}".format(hidden_count))
        print("Used Keys: {}".format(len(self.used_keys)))
        print

    def _set_words(self, words):
        if words is not None:
            self.words = words
            self._sort_words()
            print("Words Loaded: {}".format(len(self.words)))

    # ==================================================================================================================
    # Editor
    # ==================================================================================================================

    def add(self, literals):
        self.editor.add(self.words, literals)
        self.words_dirty = True

    def remove(self, literals):
        self.editor.remove(self.words, literals)
        self.words_dirty = True

    def verify(self, batch=False):
        if batch:
            self.editor.run_batch_verify(self.words)
        else:
            self.editor.run_verify(self.words)
        self.words_dirty = True

    def hide(self, literals):
        self.editor.hide(self.words, literals)
        self.words_dirty = True

    # ==================================================================================================================
    # Generator
    # ==================================================================================================================

    def _calibrate(self):
        if self.words_dirty:
            print
            print("Calibrating Words. Please wait (this could take a minute)...")
            print
            self.words_dirty = False
            self.generator.calibrate(self.words)
            self.generator.reset_flags(self.used_keys)
            self.generator.print_stats()

    def generate(self):

        self._calibrate()
        self.generator.set_output_dir(self.db_path)

        print("Generating Puzzles to CSV. Please wait...")

        self.make_level(count=1, block_def=[
            BlockDef(tier=3, count=7),
            BlockDef(tier=4, count=3),
        ])

        self.make_level(count=9, block_def=[
            BlockDef(tier=4, count=7),
            BlockDef(tier=5, count=3),
        ])

        self.make_level(count=15, block_def=[
            BlockDef(tier=5, count=10, n_min=4)
        ])

        self.make_level(count=10, block_def=[
            BlockDef(tier=6, count=10, n_min=4)
        ])

        self.make_level(count=5, block_def=[
            BlockDef(tier=6, count=10, n_min=5, percentile=0.15)
        ])

        self.generator.write_used_keys()
        self.generator.write_hidden_words()
        self.generator.write_valid_words()
        print("Puzzles generated to {}".format(self.generator.output_dir))

    def make_level(self, count, block_def):
        for i in range(count):
            puzzle_name = "Puzzle Name"
            puzzle_block = self.generator.make_puzzle_block(puzzle_name, block_def, 0,
                                                            batch=self.K_PUZZLE_BATCH,
                                                            cadence_split=0.8)
            self.generator.write_puzzle_block_to_csv(puzzle_block)

    def inspect(self, string):
        self._calibrate()
        self.generator.analyse(string)

    def generate_single(self, word_length):
        self._calibrate()
        self.generator.get_single_puzzle(word_length)

    # ==================================================================================================================
    # Utils
    # ==================================================================================================================

    def _sort_words(self):
        self.words.sort(key=lambda w: w.literal)
