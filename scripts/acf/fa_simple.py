import sys
import pickle
sys.path.append("../../")

import mir3.data.feature_track as track
import mir3.modules.features.stats as feat_stats
from feature_aggregation import FeatureAggregator


class SimpleAggregator(FeatureAggregator):
    """
    This feature aggregator is simply a front-end to the pymir3 stats module.
    """

    def __init__(self):
        """
        Nothing special here.
        """
        pass

    def aggregate(self, feature_files):
        """
        This aggregator is a front-end to the pymir3 stats module. The statistics that must be computed
        are found in the simple_aggregation key in the experiment file.

        :param feature_files: a list of FeatureTrack filenames
        :type feature_files: list[str]
        :return:
        :rtype: None

        .. note::
            These keys are expected to be set in the experiment file:
                * ['simple_aggregation']['mean']
                * ['simple_aggregation']['delta']
                * ['simple_aggregation']['variance']
                * ['simple_aggregation']['acceleration']
                * ['simple_aggregation']['slope']
                * ['simple_aggregation']['limits']
                * ['simple_aggregation']['csv']
                * ['simple_aggregation']['normalize']
                * ['general']['scratch_directory']
                * ['feature_aggregation']['aggregated_output']

        """
        features = []

        for i in feature_files:
            t = track.FeatureTrack()
            f = open(i, "r")
            t = t.load(f)
            features.append(t)
            f.close()

        stats = feat_stats.Stats()
        m = stats.stats(features,
                        mean=self.params['simple_aggregation']['mean'],
                        delta=self.params['simple_aggregation']['delta'],
                        variance=self.params['simple_aggregation']['variance'],
                        acceleration=self.params['simple_aggregation']['acceleration'],
                        slope=self.params['simple_aggregation']['slope'],
                        limits=self.params['simple_aggregation']['limits'],
                        csv=self.params['simple_aggregation']['csv'],
                        normalize=self.params['simple_aggregation']['normalize'])

        out = open(self.params['general']['scratch_directory'] +
                   "/" + self.params['feature_aggregation']['aggregated_output'], "w")

        m.save(out)

        out.close()
