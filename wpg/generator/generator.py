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
    def __init__(self, tier_falloff_count=20):
        self.tier_manager = TierManager(9, tier_falloff_count)
        self.block_id = 0
        self.output_dir = None
        self._puzzle_index = 0
        self.hidden_word_list = []
        self.valid_word_list = []

    def set_output_dir(self, output_dir):
        self.output_dir = os.path.join("./output/", output_dir)
        self._setup_output_dir()

    def calibrate(self, words):
        self.tier_manager.clear()
        self.suffix_suppression(words)
        for word in words:
            bucket = self.get_bucket(word.key, True)
            if bucket is not None:
                if word.playable:
                    bucket.add_word(word)
                elif word.valid and word.verified:
                    # Add all the hidden and suppressed words.
                    bucket.add_hidden_word(word)

        self.calibrate_buckets()

    @staticmethod
    def suffix_suppression(words):
        """ Our suppression policy will hide words that match a certain pattern. """
        patterns = ["s", "ed", "y"]
        playable_words = [w for w in words if w.playable]

        # Create a Dict of valid words.
        valid_words_dict = {}
        for w in playable_words:
            valid_words_dict[w.literal] = w

        suppress_count = 0
        for w1 in playable_words:
            for p in patterns:
                p_len = len(p)
                lit = w1.literal
                p_word = lit[-p_len:]
                if p_word == p:
                    base_word = lit[:-p_len]
                    if len(base_word) < 3:
                        continue
                    if base_word in valid_words_dict:
                        suppress_count += 1
                        w1.suppressed = True

        print("Suppressed {} Words".format(suppress_count))

    def get_bucket(self, key, create=False):
        return self.tier_manager.get_bucket(key, create)

    def calibrate_buckets(self):
        self.tier_manager.link_sub_buckets()

    def reset_flags(self, used_keys):
        self.block_id = 0
        self._puzzle_index = 0
        self.hidden_word_list = []
        self.valid_word_list = []
        self.tier_manager.reset()
        for tier in self.tier_manager.tiers:
            for key in tier.buckets:
                if key in used_keys:
                    tier.buckets[key].active = False

    def make_puzzle_block(self, name, block_defs, block_id=0, collision_cap=100, batch=10, cadence_split=0.8):
        if block_defs is None or len(block_defs) == 0:
            raise Exception("Must send in a dict for block_def")
        if block_id == 0:
            self.block_id += 1
            block_id = self.block_id

        puzzles = []
        collision_buckets = []

        for block_def in block_defs:
            print("")
            print("Block Def | ID: {} T:{}".format(block_id, block_def.n_min))
            for i in range(block_def.count):
                puzzle, bucket = self.make_single_puzzle_sans_collision(
                    block_def.tier, block_def.percentile, collision_buckets, batch, block_def.n_min)
                puzzles.append(puzzle)
                print("\tPuzzle | K: {} W: {} GS: {}".format(
                    puzzle.key, len(puzzle.words), puzzle.generator_score))
                collision_buckets.append(bucket)
                if len(collision_buckets) > collision_cap:
                    collision_buckets.pop(0)
        print("")

        sorted_puzzles = sorted(puzzles, key=lambda x: x.score)

        # Cadence the puzzles based on the split ratio.
        cadence_index = int(len(sorted_puzzles) * cadence_split)
        if cadence_index > 3:  # Cadence index must be at least 4 for any effect.

            # Split this section into two different groups.
            cadence_sorted_even = []
            cadence_sorted_odd = []

            cadence_unsorted = sorted_puzzles[:cadence_index]
            for i in range(cadence_index):
                add_list = cadence_sorted_even if i % 2 == 0 else cadence_sorted_odd
                add_list.append(cadence_unsorted[i])

            # Add all the sorted puzzles together.
            sorted_puzzles = cadence_sorted_even + cadence_sorted_odd + sorted_puzzles[cadence_index:]

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

        file_name = os.path.join(self.output_dir, self.generate_debug_file_name(puzzle_block.id))
        with open(file_name, 'wb') as f:
            csv_writer = csv.writer(f, delimiter=',')
            csv_writer.writerow([puzzle_block.name])

            for puzzle in puzzle_block.puzzles:

                # Write the key.
                key = unicode(puzzle.key).encode("utf-8")
                csv_writer.writerow(["Key: {}".format(key)])

                # Write the joined words.
                word_joined = " ".join([unicode(w).encode("utf-8") for w in puzzle.words])
                word_joined = "Puzzle Words: {}".format(word_joined)
                csv_writer.writerow([word_joined])

                # Write the hidden words.
                hidden_words = self.get_hidden_words(puzzle.key)
                word_joined = " ".join([unicode(w).encode("utf-8") for w in hidden_words])
                word_joined = "Hidden Words: {}".format(word_joined)
                csv_writer.writerow([word_joined])
                csv_writer.writerow(["Collision Score: {}".format(puzzle.collision_score)])
                csv_writer.writerow(["Puzzle Score: {}".format(puzzle.generator_score)])

                # New line.
                csv_writer.writerow(["\n"])

                # Create a list of universal hidden words for all puzzles.
                for h in hidden_words:
                    if h not in self.hidden_word_list:
                        self.hidden_word_list.append(h)

                for v in puzzle.words:
                    if v not in self.valid_word_list:
                        self.valid_word_list.append(v)

    def write_used_keys(self):
        file_name = os.path.join(self.output_dir, "used_keys")
        with open(file_name, 'wb') as file:
            csv_writer = csv.writer(file, delimiter=',')
            used_keys = self.tier_manager.get_used_keys()
            for key in used_keys:
                csv_writer.writerow([key])

    @staticmethod
    def generate_block_file_name(block_id):
        return "puzzle_block_{}.csv".format(block_id)

    @staticmethod
    def generate_debug_file_name(block_id):
        return "debug_block_{}.csv".format(block_id)

    def make_single_puzzle_sans_collision(self, word_length=5, percentile=0.5, buckets=None, batch=10, n_min=0):
        # Generate [batch] number of random puzzles, and pick the one with the least collisions to the words.

        skip_collision = False
        if buckets is None or len(buckets) == 0:
            skip_collision = True

        # Create n puzzles and find the score for each one.
        best_collision_score = 9999
        best_puzzle_score = 0
        best_bucket = 0
        collision_factor = 1.0
        collision_decay = 1.0

        for i in range(batch):

            bucket_collision_score = 0
            bucket = self.get_random_bucket(word_length, percentile, n_min)

            if bucket is None:
                raise Exception("Error: Unable to find a bucket with {} length words.".format(word_length))

            bucket_puzzle_score = bucket.n_min_score(n_min)

            if not skip_collision:
                for cmp_bucket in buckets:
                    bucket_collision_score += util.lexi_collisions(cmp_bucket, bucket, n_min) * collision_factor
                    collision_factor *= collision_decay

            if bucket_collision_score < best_collision_score or \
                    (bucket_collision_score == best_collision_score and bucket_puzzle_score > best_puzzle_score):
                best_bucket = bucket
                best_collision_score = bucket_collision_score
                best_puzzle_score = bucket_puzzle_score

        best_bucket.active = False
        puzzle = Puzzle(best_bucket.key, best_bucket.get_word_values(n_min), best_bucket.sort_score(n_min),
                        collision_score=best_collision_score, generator_score=best_bucket.n_min_score(n_min))
        return puzzle, best_bucket

    def make_single_puzzle(self, word_length=5, percentile=0.3, n_min=0):
        bucket = self.get_random_bucket(word_length, percentile, n_min)
        if bucket is None:
            raise Exception("Error: Unable to find a bucket with {} length words.".format(word_length))
        bucket.active = False
        puzzle = Puzzle(bucket.key, bucket.get_word_values(n_min), bucket.sort_score(n_min),
                        collision_score=0, generator_score=bucket.n_min_score(n_min))
        return puzzle, bucket

    def get_single_puzzle(self, word_length=5, percentile=0.3, n_min=0):
        puzzle, bucket = self.make_single_puzzle(word_length, percentile, n_min)
        key = unicode(puzzle.key).encode("utf-8")
        word_joined = " ".join([unicode(w).encode("utf-8") for w in puzzle.words])
        print("KEY: {}".format(key))
        print("WORDS: {}".format(word_joined))
        print

    def get_random_bucket(self, key_length=5, percentile=0.3, n_min=0):
        tier = self.tier_manager.get_tier(key_length)
        tier.sort_bucket_array(n_min)
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
            used_percent = 100 * sum(1 for b in tier.bucket_array if not b.active)/len(tier.bucket_array)
            print("Tier {}: {} Buckets - Used: ({:.1f}%)".format(
                i,
                len(tier.buckets),
                used_percent
            ))
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

    def write_hidden_words(self):
        """ Write all the hidden words for this generator to the file. """
        hidden_path = os.path.join(self.output_dir, "all_hidden_words")
        if os.path.exists(hidden_path):
            os.remove(hidden_path)
        hidden_file = open(hidden_path, "w+")

        for word in self.hidden_word_list:
            hidden_file.write(word + "\n")

    def write_valid_words(self):
        """ Write all the hidden words for this generator to the file. """
        write_path = os.path.join(self.output_dir, "all_valid_words")
        if os.path.exists(write_path):
            os.remove(write_path)
        valid_file = open(write_path, "w+")

        for word in self.valid_word_list:
            valid_file.write(word + "\n")

    def get_hidden_words(self, key, n_min=0):
        hidden_words = self.tier_manager.get_bucket(key).get_hidden_word_values(n_min)
        return hidden_words
