import argparse
import copy
import numpy
import scipy.stats
import sys

import mir3.data.feature_track as track
import mir3.module
import mir3.lib.naive_bayes as bayes
import mir3.lib.median_filtering as median

class Texture(mir3.module.Module):
    def get_help(self):
        return """Searching structure using textures and a naive bayesian approach"""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""input feature track""")

        parser.add_argument('-s','--start', action='append', type=float,
                            help="""start of desired structure (s) (default:
                            %(default)s)""")
        parser.add_argument('-e','--end', action='append', type=float,
                            help="""end of desired structure (s) (default:
                            %(default)s)""")

    def run(self, args):
        o = track.FeatureTrack()
        o = o.load(args.infile)

        std_o = o.data.std(axis=0)
        o.data = (o.data - o.data.mean(axis=0))/\
                    numpy.maximum(10**(-6), std_o)
                
        fs = o.metadata.sampling_configuration.ofs

        # Estimating model
        training_data = None
        max_window = 0
        for n in xrange(len(args.start)):
            t0 = int(args.start[n] * fs)
            t1 = int(args.end[n] * fs)
            if (t1 - t0) > max_window:
                max_window = t1 - t0
                
            if training_data is None:
                training_data = o.data[t0:t1,:]
            else:
                new_training_data = o.data[t0:t1,:]
                training_data = numpy.vstack((training_data, new_training_data))
        
        testing_data = median.median_filter(o.data, max_window)
        
        # Applying model in a sliding window
        output = numpy.array(bayes.naive_bayes
                          (testing_data, training_data))
        for T0 in xrange(output.shape[0]):
            print T0/float(fs), " ", output[T0]

