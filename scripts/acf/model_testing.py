# -*- coding: utf-8 -*-
import importlib
import gc
import time
from multiprocess import Pool
import acf_utils
import copy

class ModelTester:
    def __init__(self):
        pass

    @staticmethod
    def create(params):
        return acf_utils.behavior_factory(params, 'model_testing', 'model_tester', 'tst_')

    def run(self):
        pass

    def test(self, test_data):
        raise NotImplementedError