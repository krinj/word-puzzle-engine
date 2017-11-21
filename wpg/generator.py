import sqlite3

from wpg import util
from wpg.puzzle import Puzzle
from wpg.tier import TierManager
from wpg.word import Word

import random
import csv
import os
import shutil
import pickle


class PuzzleBlock:
    def __init__(self, block_id, puzzles, name):
        self.id = block_id
        self.puzzles = puzzles
        self.name = name


class Generator:
    def __init__(self):
        self.min_word_length = 2
        self.max_word_length = 7
        self.tier_manager = TierManager(8)
        self.block_id = 0
        self.output_dir = "output/bin/"
        self._setup_output_dir()

    def set_output_dir(self, output_dir):
        self.output_dir = "output/" + output_dir
        self._setup_output_dir()

    def import_data(self, input_db):
        conn = sqlite3.connect(input_db)
        cursor = conn.cursor()

        results = cursor.execute("SELECT * FROM word")
        for row in results:
            self.add_word(row[0], row[1])

        conn.commit()
        conn.close()

    def add_word(self, string, score=0):
        if len(string) < 2 or len(string) > 7:
            return
        word = Word(string, 1, score)
        bucket = self.get_bucket(word.key, True)
        bucket.add_word(word)

    def get_bucket(self, key, create=False):
        return self.tier_manager.get_bucket(key, create)

    def calibrate_buckets(self):
        self.tier_manager.link_sub_buckets()

    def reset_flags(self):
        self.block_id = 0
        self.tier_manager.reset()

    # ---------------------------------------------------------------

    def save(self, path="save/generator_data"):
        file_object = open(path, 'wb')
        pickle.dump(self.tier_manager, file_object)
        file_object.close()

    def load(self, path="save/generator_data"):
        file_object = open(path, 'r')
        self.tier_manager = pickle.load(file_object)
        file_object.close()

    # ---------------------------------------------------------------

    def make_puzzle_block(self, name, block_def, block_id=0, percentile=0.3, collision_cap=2, batch=10):
        if block_def is None:
            raise Exception("Must send in a dict for block_def")
        if block_id == 0:
            self.block_id += 1
            block_id = self.block_id

        puzzles = []
        collision_words = []
        for key in block_def:
            k_count = key
            i_count = block_def[key]
            for i in range(i_count):
                puzzle = self.make_single_puzzle_sans_collision(k_count, percentile, collision_words, batch)
                puzzles.append(puzzle)
                collision_words.insert(0, puzzle.key)
                if len(collision_words) > collision_cap:
                    collision_words.pop()

        puzzle_block = PuzzleBlock(block_id, puzzles, name)
        return puzzle_block

    def write_puzzle_block_to_csv(self, puzzle_block):
        file_name = self.output_dir + self.generate_block_file_name(puzzle_block.id)
        with open(file_name, 'wb') as file:
            csv_writer = csv.writer(file, delimiter=',')
            csv_writer.writerow([puzzle_block.name])
            csv_writer.writerow(['key', 'words', 'sub_words'])
            for puzzle in puzzle_block.puzzles:
                key = unicode(puzzle.key).encode("utf-8")
                word_joined = " ".join([unicode(w).encode("utf-8") for w in puzzle.words])
                csv_writer.writerow([key, word_joined])

    def generate_block_file_name(self, block_id):
        return "puzzle_block_{}.csv".format(block_id)

    def make_single_puzzle_sans_collision(self, word_length=5, percentile=0.3, words=[], batch=10):
        # Generate [batch] number of random puzzles, and pick the one with the least collisions to the words.

        if len(words) == 0:
            return self.make_single_puzzle(word_length, percentile)

        # Create n puzzles and find the score for each one.
        best_score = 9999
        best_bucket = 0
        for i in range(batch):
            bucket_score = 0
            bucket = self.get_random_bucket(word_length, percentile)
            for word in words:
                bucket_score += util.lexi_collisions(word, bucket.key)
            if bucket_score < best_score:
                best_bucket = bucket
                best_score = bucket_score

        best_bucket.active = False
        puzzle = Puzzle(best_bucket.key, best_bucket.get_word_values())
        return puzzle

    def make_single_puzzle(self, word_length=5, percentile=0.3):
        bucket = self.get_random_bucket(word_length, percentile)
        bucket.active = False
        puzzle = Puzzle(bucket.key, bucket.get_word_values())
        return puzzle

    def get_single_puzzle(self, word_length=5, percentile=0.3):
        puzzle = self.make_single_puzzle(word_length, percentile)
        key = unicode(puzzle.key).encode("utf-8")
        word_joined = " ".join([unicode(w).encode("utf-8") for w in puzzle.words])
        print("KEY: {}".format(key))
        print("WORDS: {}".format(word_joined))

    def get_random_bucket(self, key_length=5, percentile=0.3):
        tier = self.tier_manager.get_tier(key_length)
        tier.sort_bucket_array()
        top_index = int(len(tier.bucket_array) * percentile)
        sub_list = tier.bucket_array[0:top_index]
        bucket = random.choice(sub_list)
        return bucket

    def _setup_output_dir(self):
        try:
            shutil.rmtree(self.output_dir)
        except:
            pass
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    # ---------------------------------------------------------------
    # HELPER TEST FUNCTIONS

    def print_stats(self):
        print("--------- GENERATOR STATS ---------")
        for i in range(len(self.tier_manager.tiers)):
            tier = self.tier_manager.get_tier(i)
            if len(tier.buckets) == 0:
                continue

            print("Tier {}: {} Buckets".format(i, len(tier.buckets)))

    def top_n_buckets(self, tier_index=5, n=5):
        print("Getting Top {} Buckets from Tier {}".format(n, tier_index))
        tier = self.tier_manager.get_tier(tier_index)
        buckets = tier.get_top_n_buckets(n)
        for bucket in buckets:
            self.analyse(bucket.key)
            print(" ====================================== ")
        return buckets

    def analyse(self, string):
        print(u"Analysing String: {}".format(string))

        key = (util.get_key(string))
        print(u"Key: {}".format(key))

        bucket = self.get_bucket(key)
        print("Sub Bucket Count: {}".format(len(bucket.sub_buckets)))

        words = bucket.get_word_values()
        print("Word Count: {}".format(len(words)))
        print(u"Words: {}".format(", ".join(words)))
