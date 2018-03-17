import math
import random

import os

import sys


class AlphaGroup:
    def __init__(self, key):
        self.key = key
        self.words = []
        self.count = 0
        self.words_per_split = 0

    def add(self, word):
        self.words.append(word)
        self.count += 1

    def shuffle(self):
        random.shuffle(self.words)

    def calculate_words_per_split(self, max_splits):
        self.words_per_split = int(math.floor((1.0 * self.count)/max_splits))
        print("{}: WPS {}, MAX {}".format(self.key, self.words_per_split, len(self.words)))

    def get_words(self, split_index, final_part=False):
        w = self.words_per_split
        i = split_index
        if not final_part:
            return self.words[w * i:w * (i + 1)]
        else:
            return self.words[w * i:]


class FileSplitter:
    def __init__(self, name, min_n, max_n):
        self.alpha_groups = {}
        self.path = "./split_output/"
        self.create_output_path()
        name = name.split(".")[0]
        self.split_name = "{}_{}{}".format(name, min_n, max_n)

    def create_output_path(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def save_output_words(self, i, words):
        text_path = os.path.join(self.path, "{}_p{}.txt".format(self.split_name, str(i+1)))
        if os.path.exists(text_path):
            os.remove(text_path)
        text_file = open(text_path, "w+")
        for word in words:
            text_file.write(word.literal + "\n")

    def process(self, words, unit_count):
        print("Processing Split for {} words.".format(len(words)))
        self.sort_words_into_alpha_groups(words)
        print("Words Sorted into {} groups".format(len(self.alpha_groups)))

        split_count = int(math.ceil((1.0 * len(words)) / unit_count))
        print("Words will be split into {} file(s).".format(split_count))

        for _, alpha_group in self.alpha_groups.items():
            alpha_group.shuffle()
            alpha_group.calculate_words_per_split(split_count)

        # smallest_group, largest_group = self.get_small_large_groups()
        # print("Smallest group: {}, {} words.".format(smallest_group.key, smallest_group.count))
        # print("Largest group: {}, {} words.".format(largest_group.key, largest_group.count))

        # Calculate each groups's split ratio.
        for i in range(split_count):
            split_words = []
            is_final = i == split_count - 1
            for _, alpha_group in self.alpha_groups.items():
                alpha_words = alpha_group.get_words(split_index=i, final_part=is_final)
                split_words = split_words + alpha_words
            self.save_output_words(i, split_words)

        pass

    def get_alpha_group(self, letter):
        if letter not in self.alpha_groups.keys():
            self.alpha_groups[letter] = AlphaGroup(letter)
        return self.alpha_groups[letter]

    def sort_words_into_alpha_groups(self, words):
        for word in words:
            letter = word.literal[0]
            alpha_group = self.get_alpha_group(letter)
            alpha_group.add(word)

    def get_small_large_groups(self):
        smallest_group = None
        largest_group = None
        for _, alpha_group in self.alpha_groups.items():
            if smallest_group is None or smallest_group.count > alpha_group.count:
                smallest_group = alpha_group
            if largest_group is None or largest_group.count < alpha_group.count:
                largest_group = alpha_group
        return smallest_group, largest_group