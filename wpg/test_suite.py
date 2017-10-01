from word import Word
from wpg.bucket import Bucket


def run_tests():
    test_words()
    test_buckets()
    pass


def test_buckets():
    print("TESTING: BUCKETS -------")
    t_bucket_creation()
    print("Bucket Tests: PASSED")


def t_bucket_creation():
    b = Bucket("abc")
    if b.key != "abc":
        raise Exception("TEST FAILED")
    if b.count != 3:
        raise Exception("TEST FAILED")
    print("t_bucket_creation: PASSED")


def test_words():
    print("TESTING: WORDS -------")
    t_word_to_key()
    print("Word Tests: PASSED")


def t_word_to_key():
    w = Word("apple")
    key = w.key
    if key != "aelpp":
        raise Exception("TEST FAILED")
    print("t_word_to_key: PASSED")


if __name__ == "__main__":
    run_tests()
