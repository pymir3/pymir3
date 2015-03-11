import argparse
import copy
import numpy
import scipy.stats
import sys

import mir3.data.feature_matrix as feature_matrix
import mir3.data.feature_track as track
import mir3.module

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
        model_mean = o.data[t0:t1,:].mean(axis=0)
        model_var = o.data[t0:t1,:].var(axis=0)
        model = numpy.hstack( (model_mean, model_var) )

        
        # Applying model in a sliding window
        delta_T = t1-t0
        output = numpy.zeros( (o.data.shape[0]-delta_T, 2) )
        for T0 in xrange(output.shape[0]):
            T1 = T0 + delta_T
            this_mean = o.data[T0:T1,:].mean(axis=0)
            this_var = o.data[T0:T1,:].var(axis=0)
            this = numpy.hstack( (this_mean, this_var) )
            distance = numpy.linalg.norm(model-this)
            print T0/float(fs), " ", distance
            #output[T0,0] = T0 / fs
            #output[T0,1] = distance

