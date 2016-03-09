import argparse
import copy
import numpy
import scipy.stats
import sys

import mir3.data.feature_matrix as feature_matrix
import mir3.data.feature_track as track
import mir3.module

class Stats(mir3.module.Module):
    def get_help(self):
        return """Statistics from a track. Will print on screen."""

    def build_arguments(self, parser):
        parser.add_argument('infiles', nargs='+', type=argparse.FileType('rb'),
                            help="""input track files""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""output file""")

        parser.add_argument('-m','--mean', action='store_true', default=False,
                            help="""output mean (default:
                            %(default)s)""")
        parser.add_argument('-v','--variance', action='store_true',
                            default=False, help="""output variance (default:
                            %(default)s)""")
        parser.add_argument('-s','--slope', action='store_true', default=False,
                            help="""output slope (default:
                            %(default)s)""")
        parser.add_argument('-l','--limits', action='store_true', default=False,
                            help="""output maximum and minimum, including their
                            positions in fraction of the full track length
                            (default: %(default)s)""")
        parser.add_argument('-c','--csv', action='store_true', default=False,
                            help="""csv-output (default:
                            %(default)s)""")
        parser.add_argument('-n','--normalize', action='store_true',
                            default=False, help="""normalize each output column
                            to 0 mean and unit variance (default:
                            %(default)s)""")

    def stats(self, feature_tracks, mean=False, variance=False, slope=False, limits=False, csv=False, normalize=False):

        final_output = None
        final_filenames = []

        for o in feature_tracks:

            #print o.metadata.feature

            a = numpy.array(o.metadata.feature.split())
            i = a.argsort()

            final_filenames.append(o.metadata.filename)
            if o.data.ndim == 1:
                o.data.shape = (o.data.size, 1)

            out = numpy.array([])
            if mean is True:
                out = numpy.hstack((out,
                             o.data.mean(axis=0)[i]))

#            print out.shape

            if variance is True:
                out = numpy.hstack((out,
                             o.data.var(axis=0)[i]))

#            print out.shape
            if slope is True:
                variance = o.data.var(axis=0)[i]
                lindata = numpy.zeros(variance.shape)
                for i in xrange(o.data.shape[1]):
                    lindata[i] = scipy.stats.linregress(o.data[:,i],\
                                            range(o.data.shape[0]))[0]

                out = numpy.hstack((out,lindata))

            if limits is True:
                out = numpy.hstack((out,
                             o.data.max(axis=0)[i]))
                out = numpy.hstack((out,
                             o.data.argmax(axis=0)[i]/float(o.data.shape[0])))
                out = numpy.hstack((out,
                             o.data.min(axis=0)[i]))
                out = numpy.hstack((out,
                             o.data.argmin(axis=0)[i]/float(o.data.shape[0])))

                out.shape = (1, out.size)

            if csv is True:
                for i in xrange(len(out)-1):
                    sys.stdout.write(str(out[i]))
                    sys.stdout.write(",")
                sys.stdout.write(str(out[-1]))
                sys.stdout.write('\n')

            if final_output is None:
                final_output = out
            else:
                final_output = numpy.vstack( (final_output, out) )

        # Dealing with feature metadata:
        my_features = o.metadata.feature.split()
        my_features.sort()
        new_features = ""
        if mean is True:
            for feat in my_features:
                new_features = new_features + " " + "mean_" + feat
        if variance is True:
            for feat in my_features:
                new_features = new_features + " " + "var_" + feat
        if slope is True:
            for feat in my_features:
                new_features = new_features + " " + "slope_" + feat
        if limits is True:
            for feat in my_features:
                new_features = new_features + " " + "max_" + feat
            for feat in my_features:
                new_features = new_features + " " + "argmax_" + feat
            for feat in my_features:
                new_features = new_features + " " + "min_" + feat
            for feat in my_features:
                new_features = new_features + " " + "argmin_" + feat

        p = feature_matrix.FeatureMatrix()
        p.data = final_output.copy()

        if normalize:
            std_p = p.data.std(axis=0)
            p.data = (p.data - p.data.mean(axis=0))/\
                    numpy.maximum(10**(-6), std_p)

        p.metadata.sampling_configuration = o.metadata.sampling_configuration
        p.metadata.feature = new_features
        p.metadata.filename = final_filenames

        return p

    def run(self, args):
        print "Calculating stats..."
        feature_tracks = []

        for a in args.infiles:
            f = track.FeatureTrack()
            f = f.load(a)
            feature_tracks.append(f)

        p = self.stats(feature_tracks, args.mean, args.variance, args.slope, args.limits, args.csv, args.normalize)

        p.save(args.outfile)
