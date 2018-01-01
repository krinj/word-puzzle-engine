class Bucket:
    def __init__(self, key):
        self.key = key
        self.count = len(key)
        self.words = []
        self.sub_buckets = []
        self.sub_word_count = 0
        self.sub_word_score = 0
        self.active = True

    def add_word(self, word):
        self.words.append(word)
        self._add_word_score(word)

    def add_sub_bucket(self, sub_bucket):
        if sub_bucket not in self.sub_buckets:
            self.sub_buckets.append(sub_bucket)
            for word in sub_bucket.words:
                self._add_word_score(word)

    def _add_word_score(self, word):
        self.sub_word_count += 1
        if len(word.literal) > 3:
            self.sub_word_score += 2
        else:
            self.sub_word_score += 1

    def get_word_values(self):
        out_words = []
        for s_bucket in self.sub_buckets:
            for word in s_bucket.words:
                out_words.append(word.literal)

        for word in self.words:
            out_words.append(word.literal)

        out_words.sort(key=lambda item: (len(item), item))
        return out_words

    def reset(self):
        self.active = True

