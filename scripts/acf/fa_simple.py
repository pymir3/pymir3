import sys
import pickle
sys.path.append("../../")

import mir3.modules.tool.to_texture_window as texture_window
import mir3.data.feature_track as track
import mir3.modules.features.stats as feat_stats
from feature_aggregation import FeatureAggregator
from multiprocess import Pool
import time
import traceback
import gc
from pprint import pprint

def calc_textures(args):
    try:

        tw = texture_window.ToTextureWindow()
        feature = args[0]
        print("calculating textures for %s" % feature.metadata.filename)
        T0 = time.time()
        results = tw.to_texture(feature, args[1])
        T1 = time.time()
        print("texture calculation for %s took %f seconds" % (feature.metadata.filename, T1-T0))
        return results

    except Exception:
            traceback.print_exc()
            raise

def load_feature_files(feature_files):
    features = []

    for i in feature_files:
        t = track.FeatureTrack()
        f = open(i, "r")
        t = t.load(f)
        features.append(t)
        f.close()

    return features

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

        features = load_feature_files(feature_files)

        if self.params['simple_aggregation']['texture_windows']:

            #for i in range(len(feature_files)):
            #    feature_files[i] = feature_files[i] + "_tw"

            jobs = []
            for f in features:
                jobs.append((f, self.params['simple_aggregation']['texture_window_length']))

            num_files = len(jobs)
            output_buffer_size = self.params['simple_aggregation']['tw_buffer_size']

            pool = Pool(processes=self.params['simple_aggregation']['tw_workers'])

            out_idx = 0

            for i in range(0, num_files, output_buffer_size):
                print "Calculating texture windows %d through %d of %d" % (i + 1, min(i + output_buffer_size, num_files), num_files)
                
                result = pool.map(calc_textures, jobs[i:min(i + output_buffer_size, num_files)])
                
                for track in result:
                    filename = feature_files[out_idx]
                    print "writing features to file %s..." % (filename)
                    feature_file = open(filename, "w")
                    track.save(feature_file)
                    feature_file.close()
                    del track
                    out_idx+=1

                del result
                gc.collect()

            pool.close()
            pool.join()
            features = None

        if features == None:
            features = load_feature_files(feature_files)

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

#if not os.path.exists(clipped_folder):
#        os.makedirs(clipped_folder)
