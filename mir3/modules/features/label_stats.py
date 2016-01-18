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
        return """Statistics from a track based on a label file. Will calculate
    statistics for each region defined in the label file."""

    def build_arguments(self, parser):
        parser.add_argument('trackfile', type=argparse.FileType('rb'),
                            help="""input track file""")
        parser.add_argument('labelfile', type=str,
                            help="""input track file""")
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

    def run(self, args):
        o = track.FeatureTrack()
        o.load(args.trackfile)

        # Read label file
        onsets = []
        offsets = []
        labels = []
        with open(args.labelfile) as f:
            content = f.readlines()
            for line in content:
                L = line.split()
                onsets.append(float(L[0]))
                offsets.append(float(L[1]))
                L[2].replace('-', '+')
                labels.append(str(L[2].split('+')[0]))
                print onsets[-1], offsets[-1], labels[-1]
        exit()

        final_output = None
        final_filenames = []

        for a in args.infiles:
            o = o.load(a)

            #print o.metadata.feature

            a = numpy.array(o.metadata.feature.split())
            i = a.argsort()

            #print a
            #print o.data.mean(axis=0)

            #print i
            #print a[i]
            #print o.data.mean(axis=0)[i], "\n"

 #           print o.data.shape

            final_filenames.append(o.metadata.filename)
            if o.data.ndim == 1:
                o.data.shape = (o.data.size, 1)

            out = numpy.array([])
            if args.mean is True:
                out = numpy.hstack((out,
                             o.data.mean(axis=0)[i]))

#            print out.shape

            if args.variance is True:
                out = numpy.hstack((out,
                             o.data.var(axis=0)[i]))

#            print out.shape
            if args.slope is True:
                variance = o.data.var(axis=0)[i]
                lindata = numpy.zeros(variance.shape)
                for i in xrange(o.data.shape[1]):
                    lindata[i] = scipy.stats.linregress(o.data[:,i],\
                                            range(o.data.shape[0]))[0]

                out = numpy.hstack((out,lindata))

            if args.limits is True:
                out = numpy.hstack((out,
                             o.data.max(axis=0)[i]))
                out = numpy.hstack((out,
                             o.data.argmax(axis=0)[i]/float(o.data.shape[0])))
                out = numpy.hstack((out,
                             o.data.min(axis=0)[i]))
                out = numpy.hstack((out,
                             o.data.argmin(axis=0)[i]/float(o.data.shape[0])))


                out.shape = (1, out.size)

            if args.csv is True:
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
        if args.mean is True:
            for feat in my_features:
                new_features = new_features + " " + "mean_" + feat
        if args.variance is True:
            for feat in my_features:
                new_features = new_features + " " + "var_" + feat
        if args.slope is True:
            for feat in my_features:
                new_features = new_features + " " + "slope_" + feat
        if args.limits is True:
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

        if args.normalize:
            std_p = p.data.std(axis=0)
            p.data = (p.data - p.data.mean(axis=0))/\
                    numpy.maximum(10**(-6), std_p)

        p.metadata.sampling_configuration = o.metadata.sampling_configuration
        p.metadata.feature = new_features
        p.metadata.filename = final_filenames
        p.save(args.outfile)
