import csv
import os
import random
import shutil

from wpg.generator.tier import TierManager
from wpg.generator.puzzle import Puzzle
from wpg.utils import util


class PuzzleBlock:
    def __init__(self, block_id, puzzles, name):
        self.id = block_id
        self.puzzles = puzzles
        self.name = name


class Generator:
    def __init__(self):
        self.tier_manager = TierManager(9)
        self.block_id = 0
        self.output_dir = None

    def set_output_dir(self, output_dir):
        self.output_dir = os.path.join("./output/", output_dir)
        self._setup_output_dir()

    def calibrate(self, words):
        self.tier_manager.clear()
        for word in words:
            if word.verified and word.valid and not word.hidden:
                bucket = self.get_bucket(word.key, True)
                if bucket is not None:
                    bucket.add_word(word)
        self.calibrate_buckets()

    def get_bucket(self, key, create=False):
        return self.tier_manager.get_bucket(key, create)

    def calibrate_buckets(self):
        self.tier_manager.link_sub_buckets()
        self.print_stats()

    def reset_flags(self):
        self.block_id = 0
        self.tier_manager.reset()

    def make_puzzle_block(self, name, block_def, block_id=0, percentile=0.5, collision_cap=3, batch=10):
        if block_def is None:
            raise Exception("Must send in a dict for block_def")
        if block_id == 0:
            self.block_id += 1
            block_id = self.block_id

        puzzles = []
        collision_buckets = []
        for key in block_def:
            k_count = key
            i_count = block_def[key]
            for i in range(i_count):
                puzzle, bucket = self.make_single_puzzle_sans_collision(k_count, percentile, collision_buckets, batch)
                puzzles.append(puzzle)
                collision_buckets.insert(0, bucket)
                if len(collision_buckets) > collision_cap:
                    collision_buckets.pop()

        sorted_puzzles = sorted(puzzles, key=lambda x: x.score)
        puzzle_block = PuzzleBlock(block_id, sorted_puzzles, name)
        return puzzle_block

    def write_puzzle_block_to_csv(self, puzzle_block):
        file_name = os.path.join(self.output_dir, self.generate_block_file_name(puzzle_block.id))
        with open(file_name, 'wb') as file:
            csv_writer = csv.writer(file, delimiter=',')
            csv_writer.writerow([puzzle_block.name])
            csv_writer.writerow(['key', 'words', 'sub_words'])
            for puzzle in puzzle_block.puzzles:
                key = unicode(puzzle.key).encode("utf-8")
                # key = "{} {}".format(key, puzzle.score)
                word_joined = " ".join([unicode(w).encode("utf-8") for w in puzzle.words])
                csv_writer.writerow([key, word_joined])

    @staticmethod
    def generate_block_file_name(block_id):
        return "puzzle_block_{}.csv".format(block_id)

    def make_single_puzzle_sans_collision(self, word_length=5, percentile=0.5, buckets=None, batch=10):
        # Generate [batch] number of random puzzles, and pick the one with the least collisions to the words.

        if buckets is None or len(buckets) == 0:
            return self.make_single_puzzle(word_length, percentile)

        # Create n puzzles and find the score for each one.
        best_score = 9999
        best_bucket = 0
        collision_factor = 1.0
        collision_decay = 0.85

        for i in range(batch):
            bucket_score = 0
            bucket = self.get_random_bucket(word_length, percentile)
            if bucket is None:
                raise Exception("Error: Unable to find a bucket with {} length words.".format(word_length))
            for cmp_bucket in buckets:
                bucket_score += util.lexi_collisions(cmp_bucket, bucket) * collision_factor
                collision_factor *= collision_decay
            if bucket_score < best_score:
                best_bucket = bucket
                best_score = bucket_score

        best_bucket.active = False
        puzzle = Puzzle(best_bucket.key, best_bucket.get_word_values(), best_bucket.sort_score)
        return puzzle, best_bucket

    def make_single_puzzle(self, word_length=5, percentile=0.3):
        bucket = self.get_random_bucket(word_length, percentile)
        if bucket is None:
            raise Exception("Error: Unable to find a bucket with {} length words.".format(word_length))
        bucket.active = False
        puzzle = Puzzle(bucket.key, bucket.get_word_values(), bucket.sort_score)
        return puzzle, bucket

    def get_single_puzzle(self, word_length=5, percentile=0.3):
        puzzle, bucket = self.make_single_puzzle(word_length, percentile)
        key = unicode(puzzle.key).encode("utf-8")
        word_joined = " ".join([unicode(w).encode("utf-8") for w in puzzle.words])
        print("KEY: {}".format(key))
        print("WORDS: {}".format(word_joined))
        print

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
        print
        print("--------- CALIBRATION STATS ---------")
        for i in range(len(self.tier_manager.tiers)):
            tier = self.tier_manager.get_tier(i)
            if len(tier.buckets) == 0:
                continue
            print("Tier {}: {} Buckets".format(i, len(tier.buckets)))
        print

    def analyse(self, string):
        print(u"Analysing String: {}".format(string))

        key = (util.get_key(string))
        print(u"Key: {}".format(key))

        bucket = self.get_bucket(key)
        if bucket is None:
            print("No buckets found for: '{}'".format(string))
            return

        words = bucket.get_word_values()
        print("Word Count: {}".format(len(words)))
        print(u"Words: {}".format(", ".join(words)))
