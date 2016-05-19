import sys
import pickle
sys.path.append("../../")

import mir3.data.feature_track as track
import mir3.modules.features.stats as feat_stats
from feature_aggregation import FeatureAggregator


class SimpleAggregator(FeatureAggregator):

    def __init__(self):
        pass

    def aggregate(self, feature_files):

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
