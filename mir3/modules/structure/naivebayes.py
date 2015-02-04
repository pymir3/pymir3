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
        return """Searching structure using textures.."""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""input feature track""")

        parser.add_argument('-s','--start', default=0, type=float,
                            help="""start of desired structure (s) (default:
                            %(default)s)""")
        parser.add_argument('-e','--end', default=1, type=float,
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
        t0 = int(args.start * fs)
        t1 = int(args.end * fs)
        training_data = o.data[t0:t1,:]
        testing_data = median.median_filter(o.data, t1-t0)
        
        # Applying model in a sliding window
        output = numpy.array(bayes.naive_bayes
                          (testing_data, training_data))
        for T0 in xrange(output.shape[0]):
            print T0/float(fs), " ", output[T0]

