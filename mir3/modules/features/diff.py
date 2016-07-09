import argparse
import numpy

import mir3.data.feature_track as track
import mir3.module

class Diff(mir3.module.Module):
    def get_help(self):
        return """Differentiate (y[t] = x[t]-x[t-1]) a track"""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""input file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""output file""")

    def run(self, args):
        o = track.FeatureTrack().load(args.infile)
        o = self.calc_track(o)
        o.save(args.outfile)

    def calc_track(self, o):
        if o.data.ndim == 1:
            o.data.shape = (o.data.size, 1)

        pad = numpy.zeros( (1, o.data.shape[1]) )

        o.data = numpy.vstack( ( pad,
                                 numpy.diff(o.data, axis=0) ) )

        # Dealing with feature metadata:
        my_features = o.metadata.feature.split()
        new_features = ""
        for feat in my_features:
            if (len(new_features) > 2) and (new_features[-1] != " "):
                new_features += " "
            new_features = new_features + "diff_" + feat
        o.metadata.feature = new_features

        return o
