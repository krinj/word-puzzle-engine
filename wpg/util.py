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


def lexi_collisions(word1, word2):
    # Find the number of duplicate letters in the two words.
    copy_word1 = [x for x in word1]
    copy_word2 = [x for x in word2]
    collisions = 0
    for i in copy_word1:
        if i in copy_word2:
            copy_word2.remove(i)
            collisions += _get_collision_score(i)
    return collisions


def _get_collision_score(letter):
    # TODO: Adjust this for other alphabets.
    # Give lower points for vowels because they are so common.
    if letter in "aeiou":
        return 1
    else:
        return 2
