import importlib
import gc
import acf_utils
import glob


class FeatureAggregator():
    """
    This is a base class used to aggregate features from a list of feature files.
    The term aggregate in this context relates to the process of computing feature vectors for all instances.
    Its derived classes must implement the *aggregate* method.
    """

    def __init__(self):
        """
        FeatureAggregator is an abstract class. To use it you must extend it and then use the *create* static method
        as a factory.
        """
        pass

    @staticmethod
    def create(params):
        """
        This is a factory function that creates a feature aggregator derived class
        from the parameter file. It dynamically loads the requested feature aggregator class.

        :param params: A dictionary from a yaml experiment file.
        :type params: dict
        :return:
        :rtype: FeatureAggregator
        """
        return acf_utils.behavior_factory(params, 'feature_aggregation', 'aggregator', 'fa_')

    def run(self):
        """
        This function runs the feature aggregator. Specifically it passes a list of FeatureTrack file names
        to the behavior-specific aggregator class.
        """
        print("Running feature aggregation behavior: %s" % self.name)
        feature_filenames = sorted([i for i in glob.glob('scratch/*.features')])
        self.aggregate(feature_filenames)
        feature_filenames = []
        gc.collect()
        print ('Feature aggregation done!')

    def aggregate(self, feature_files):
        """
        This is an abstract method that should implement feature aggregation. This method must be implemented
        in the subclasses.

        :param feature_files: a list of FeatureTrack filenames
        :type feature_files: list[str]
        :return:
        :rtype: None
        """

        # One must implement this method in a subclass!
        raise NotImplementedError
        pass


if __name__ == "__main__":
    feature_files = sorted([i for i in glob.glob('scratch/*.features')])
    print len(feature_files)



