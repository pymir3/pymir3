import importlib
import gc
import acf_utils

class FeatureAggregator():

    def __init__(self):
        pass

    @staticmethod
    def create(params):
        return acf_utils.behavior_factory(params, 'feature_aggregation', 'aggregator', 'fa_')



