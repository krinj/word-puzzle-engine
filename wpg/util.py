from collections import Counter


def is_subset(main_word, sub_word):
    # If the sub_word exists in the main_word in any order.
    word1, word2 = Counter(main_word), Counter(sub_word)
    return all(word2[k] <= word1.get(k, 0) for k in word2)


def get_key(string=""):
    sorted_letters = sorted(string)
    key = "".join(sorted_letters)
    return key
