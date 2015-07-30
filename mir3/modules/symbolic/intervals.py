import argparse
import numpy

import mir3.data.score as score
import mir3.lib.mir.midifeatures as feats
import mir3.module

class Intervals(mir3.module.Module):
    """Calculates the interval histogram from a score"""

    def get_help(self):
        return """Pitch class histogram from a score. Prints the values on
    screen"""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""file containing score""")
        parser.add_argument('--fold', '-f', type=int, default=12,\
                help="""Number of semitones to fold spectrogram into""")
        parser.add_argument('--time_tolerance', '-t', type=float,\
                default=0.005,\
                help="""Tolerance (s) between two consecutive events so they are
                still considered simultaneous""")
        parser.add_argument('--duration', '-d', default=False,\
                action='store_true',\
                help="""Consider duration as weights when estimating""")
        parser.add_argument('--statistics', '-s', default=False,\
                action='store_true',\
                help="""Also outputs statistics (mean, std deviation,
                entropy and indexes of 4 greatest values)""")



    def run(self, args):
        s = score.Score().load(args.infile)
        events = feats.event_list(s.data)
        histogram = feats.interval_histogram(events, args.fold,\
                args.time_tolerance, args.duration)
        for i in xrange(args.fold):
            print histogram[i],

        if args.statistics is True:
            h = numpy.array(histogram)
            print numpy.mean(h),
            print numpy.std(h),
            print numpy.sum(numpy.array([h[i] * numpy.log2(h[i])\
                    for i in xrange(len(h))\
                    if h[i] > 0])),

            for i in xrange(4):
                m = numpy.argmax(h)
                print m,
                h[m] = 0

        print " "


