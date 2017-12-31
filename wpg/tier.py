import time

from wpg.bucket import Bucket
from wpg.utils import util


class Tier:
    def __init__(self, tier_id):
        self.id = tier_id
        self.lower = None
        self.higher = None
        self.buckets = {}
        self.bucket_array = []
        self.min_sub_tier_size = 2

    def get_bucket(self, key, create=False):
        if key not in self.buckets:
            if not create:
                return None
            bucket = Bucket(key)
            self.buckets[key] = bucket
            self.bucket_array.append(bucket)
        return self.buckets[key]

    def sort_bucket_array(self):
        self.bucket_array = sorted(self.bucket_array, key=lambda item: (item.active, item.sub_word_score), reverse=True)

    def get_top_n_buckets(self, n=5):
        return self.bucket_array[0:n]

    def reset(self):
        for bucket in self.bucket_array:
            bucket.reset()


class TierManager:
    def __init__(self, n_tiers=7):
        self.tiers = []
        for i in range(n_tiers):
            tier = Tier(i)
            if i > 3:
                tier.min_sub_tier_size = 3
            else:
                tier.min_sub_tier_size = 2
            if i > 0:
                tier.lower = self.tiers[i - 1]
                self.tiers[i - 1].higher = tier
            self.tiers.append(tier)

    def reset(self):
        for i in range(len(self.tiers)):
            self.tiers[i].reset()

    def get_tier(self, index):
        return self.tiers[index]

    def get_bucket(self, key, create=False):
        index = len(key)
        tier = self.tiers[index]
        return tier.get_bucket(key, create)

    def link_sub_buckets(self):
        start_time = time.time()
        for i in range(1, len(self.tiers)):
            t_start_time = time.time()
            tier = self.tiers[i]
            for big_key in tier.buckets:
                big_bucket = tier.buckets[big_key]
                for j in range(tier.min_sub_tier_size, i):
                    lower_tier = self.tiers[j]
                    for small_key in lower_tier.buckets:
                        is_subset = util.is_subset(big_key, small_key)
                        if is_subset:
                            small_bucket = lower_tier.buckets[small_key]
                            big_bucket.add_sub_bucket(small_bucket)

            t_duration = time.time() - t_start_time
            print("Tier {:.0f} Duration: {:.2f}".format(i, t_duration))

        duration = time.time() - start_time
        print("Link Sub Buckets: {:.2f}".format(duration))
