from wpg import util
from wpg.bucket import Bucket
from wpg.puzzle import Puzzle
from wpg.tier import TierManager
from wpg.word import Word
import random
import csv
import os
import shutil


class Generator:
    def __init__(self, output_dir="cookie/"):
        self.min_word_length = 2
        self.max_word_length = 7
        self.tier_manager = TierManager(8)
        self.block_id = 0
        self.output_dir = "output/" + output_dir
        self.setup_output_dir()

    def add_word(self, string, score=0):
        if len(string) < 2 or len(string) > 7:
            return
        word = Word(string, score)
        bucket = self.get_bucket(word.key, True)
        bucket.add_word(word)

    def get_bucket(self, key, create=False):
        return self.tier_manager.get_bucket(key, create)

    def calibrate_buckets(self):
        self.tier_manager.link_sub_buckets()
        pass

    def clear(self):
        pass

    def reset_flags(self):
        self.block_id = 0
        self.tier_manager.reset()

    # ---------------------------------------------------------------

    def make_puzzle_block(self, block_def, block_id=0, percentile=0.3):
        if block_def is None:
            raise Exception("Must send in a dict for block_def")
        if block_id == 0:
            self.block_id += 1
            block_id = self.block_id

        puzzles = []
        for key in block_def:
            k_count = key
            i_count = block_def[key]
            for i in range(i_count):
                puzzle = self.make_single_puzzle(k_count, percentile)
                puzzles.append(puzzle)
        self.write_puzzles_to_csv(block_id, puzzles)

    def write_puzzles_to_csv(self, block_id, puzzles):
        file_name = self.output_dir + self.generate_block_file_name(block_id)
        with open(file_name, 'wb') as file:
            csv_writer = csv.writer(file, delimiter=',')
            csv_writer.writerow(['key', 'words', 'sub_words'])
            for puzzle in puzzles:
                key = puzzle.key
                word_joined = " ".join(puzzle.words)
                csv_writer.writerow([puzzle.key, word_joined])

    def generate_block_file_name(self, block_id):
        return "puzzle_block_{}.csv".format(block_id)

    def make_single_puzzle(self, word_length=5, percentile=0.3):
        bucket = self.get_random_bucket(word_length, percentile)
        bucket.active = False
        # self.analyse(bucket.key)
        puzzle = Puzzle(bucket.key, bucket.get_word_values())
        return puzzle

    def get_random_bucket(self, key_length=5, percentile=0.3):
        tier = self.tier_manager.get_tier(key_length)
        tier.sort_bucket_array()
        top_index = int(len(tier.bucket_array) * percentile)
        sub_list = tier.bucket_array[0:top_index]
        bucket = random.choice(sub_list)
        return bucket

    def setup_output_dir(self):
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
        print("Analysing String: {}".format(string))

        key = (util.get_key(string))
        print("Key: {}".format(key))

        bucket = self.get_bucket(key)
        print("Sub Bucket Count: {}".format(len(bucket.sub_buckets)))

        words = bucket.get_word_values()
        print("Word Count: {}".format(len(words)))
        print("Words: {}".format(", ".join(words)))
