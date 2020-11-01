import pandas as pd
import os
import sys
from duplicate_detector.apps import DuplicateDetectorConfig
from duplicate_detector.predictor.utils import get_blocks_v1
import warnings

warnings.filterwarnings('ignore')


class MethodRepresentationCalculator:

    def __tree_to_index(self, node):
        token = node.token
        result = [DuplicateDetectorConfig.word2vec_vocab[
                      token].index if token in DuplicateDetectorConfig.word2vec_vocab else DuplicateDetectorConfig.MAX_TOKENS]
        children = node.children
        for child in children:
            result.append(self.__tree_to_index(child))
        return result

    def __trans2seq(self, r):
        blocks = []
        get_blocks_v1(r, blocks)
        tree = []
        for b in blocks:
            btree = self.__tree_to_index(b)
            tree.append(btree)
        return tree

    def predict_clone(self, method1, method2):
        pass
