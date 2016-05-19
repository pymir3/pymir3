import importlib
import gc
import acf_utils
import glob

class FeatureAggregator():

    def __init__(self):
        pass

    @staticmethod
    def create(params):
        return acf_utils.behavior_factory(params, 'feature_aggregation', 'aggregator', 'fa_')

    def run(self):
        feature_files = sorted([i for i in glob.glob('scratch/*.features')])
        self.aggregate(feature_files)
        print "Aggregation done!"

    def aggregate(self, feature_files):
        raise NotImplementedError
        pass


if __name__ == "__main__":
    feature_files = sorted([i for i in glob.glob('scratch/*.features')])
    print len(feature_files)



