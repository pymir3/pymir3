
import argparse
import matplotlib.pyplot as plt
import numpy

import mir3.data.feature_track as feature_track

def plot(input_filename, output_filename, scale=None, dim=0, size=(3.45,2.0)):
    """Plots the a spectrogram to an output file
    """
    s = feature_track.FeatureTrack().load(input_filename)

    if s.data.ndim > 1:
        d = s.data[:,dim]
    else:
        d = s.data

    min_y = numpy.min(d)
    max_y = numpy.max(d)
    min_time = 0
    max_time = float(len(d)) / s.metadata.sampling_configuration.ofs

    ylabel = s.metadata.feature.split()[dim]
    if scale is not None:
        ylabel += ' ('
        ylabel += str(scale)
        ylabel += ')'

    x_axis = numpy.array(range(len(d))) / \
            float(s.metadata.sampling_configuration.ofs)

    im = plt.plot(x_axis, d)
    plt.xlabel('Time (s)')
    plt.ylabel(ylabel)
    fig = plt.gcf()
    width_inches = size[0]#/80.0
    height_inches = size[1]#/80.0
    fig.set_size_inches( (width_inches, height_inches) )
    plt.savefig(output_filename, bbox_inches='tight')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot a spectrogram')
    parser.add_argument('infile', type=argparse.FileType('rb'),\
help="""Input spectrogram file""")
    parser.add_argument('outfile',\
help="""Output figure file""")
    parser.add_argument('--dim', type=int, default=0, help="""Dimension to
    plot (used in multidimensional feature tracks)""")
    parser.add_argument('--scale', default=None, help="""Scale to use in y-axis
    label""")
    parser.add_argument('--width', type=int, default=3.45, help="""Output width\
            (inches).\
            Default: 3.45 (one column)""")
    parser.add_argument('--height', type=int, default=2.0, help="""Output\
            height (inches).\
            Default: 2.0""")
    args = parser.parse_args()
    plot(args.infile, args.outfile, args.scale, args.dim, \
            (args.width, args.height))




