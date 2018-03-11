def is_subset(main_word, sub_word):
    # If the sub_word exists in the main_word in any order.
    for s in sub_word:
        if s not in main_word:
            return False
        else:
            main_word = main_word.replace(s, "", 1)
    return True


def get_key(string=""):
    sorted_letters = sorted(string)
    key = "".join(sorted_letters)
    return key


def divide_string(string, n=3):
    # Returns an array of strings, divided by n-length from the original string.
    return [string[i:i + n] for i in range(0, len(string), n)]


def strip(string, char):
    for c in char:
        string = string.replace(c, "")
    return string


def lexi_collisions(first_bucket, second_bucket):
    # Find the number of duplicate words in the two words.
    collisions = 0
    for word1 in first_bucket.words:
        for word2 in second_bucket.words:
            if word1 == word2:
                collisions += 1
    return collisions
