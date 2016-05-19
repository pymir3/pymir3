import argparse
import copy
import numpy
import scipy.stats
import scipy.signal
import sys

import mir3.data.feature_matrix as feature_matrix
import mir3.data.feature_track as track
import mir3.module


def delta_stat(data, width=9, order=1, axis=-1, trim=True):
    r'''Compute delta features: local estimate of the derivative
    of the input data along the selected axis.


    Parameters
    ----------
    data      : np.ndarray
        the input data matrix (eg, spectrogram)

    width     : int >= 3, odd [scalar]
        Number of frames over which to compute the delta feature

    order     : int > 0 [scalar]
        the order of the difference operator.
        1 for first derivative, 2 for second, etc.

    axis      : int [scalar]
        the axis along which to compute deltas.
        Default is -1 (columns).

    trim      : bool
        set to `True` to trim the output matrix to the original size.

    Returns
    -------
    delta_data   : np.ndarray [shape=(d, t) or (d, t + window)]
        delta matrix of `data`.

    FROM librosa.

    http://www1.icsi.berkeley.edu/Speech/faq/deltas.html

    '''

    data = numpy.atleast_1d(data)

    if width < 3 or numpy.mod(width, 2) != 1:
        print('width must be an odd integer >= 3')
        exit(1)

    if order <= 0 or not isinstance(order, int):
        print('order must be a positive integer')
        exit(1)

    half_length = 1 + int(width // 2)
    window = numpy.arange(half_length - 1., -half_length, -1.)

    # Normalize the window so we're scale-invariant
    window /= numpy.sum(numpy.abs(window)**2)

    # Pad out the data by repeating the border values (delta=0)
    padding = [(0, 0)] * data.ndim
    width = int(width)
    padding[axis] = (width, width)
    delta_x = numpy.pad(data, padding, mode='edge')

    for _ in range(order):
        delta_x = scipy.signal.lfilter(window, 1, delta_x, axis=axis)

    # Cut back to the original shape of the input data
    if trim:
        idx = [slice(None)] * delta_x.ndim
        idx[axis] = slice(- half_length - data.shape[axis], - half_length)
        delta_x = delta_x[idx]

    return delta_x

class Stats(mir3.module.Module):
    def get_help(self):
        return """Statistics from a track. Will print on screen."""

    def build_arguments(self, parser):
        parser.add_argument('infiles', nargs='+', type=argparse.FileType('rb'),
                            help="""input track files""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""output file""")

        parser.add_argument('-d', '--delta', action='store_true', default=False,
                            help="""output delta (default:
                            %(default)s)""")
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

    def stats(self, feature_tracks, mean=False, variance=False, delta=False, acceleration=False, slope=False, limits=False, csv=False, normalize=False):

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

            if delta is True:
                #print "o.data shape", o.data.shape
                #print "out shape ", out.shape
                d = numpy.mean(delta_stat(o.data, order=1, axis=0), axis=0)[i]
                #print "d shape ", d.shape
                out = numpy.hstack((out, d ))

            if acceleration is True:
                #print "o.data shape", o.data.shape
                #print "out shape ", out.shape
                d = numpy.mean(delta_stat(o.data, order=2, axis=0), axis=0)[i]
                #print "d shape ", d.shape
                out = numpy.hstack((out, d ))

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

        if delta is True:
            for feat in my_features:
                new_features = new_features + " " + "delta_" + feat
        if acceleration is True:
            for feat in my_features:
                new_features = new_features + " " + "accel_" + feat
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

        #print new_features

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
