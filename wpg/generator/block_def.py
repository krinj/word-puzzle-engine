# -*- coding: utf-8 -*-

"""
block_def | wp-gen | 20/06/18
The puzzle block definition, to guide the creation of a puzzle block.
"""

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class BlockDef:
    def __init__(self, tier, count, n_min=0, percentile=0.35):
        self.tier = tier
        self.n_min = n_min
        self.count = count
        self.percentile = percentile
