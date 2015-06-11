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




    def run(self, args):
        s = score.Score().load(args.infile)
        events = feats.event_list(s.data)
        histogram = feats.interval_histogram(events, args.fold,\
                args.time_tolerance, args.duration)
        for i in xrange(args.fold):
            print histogram[i],
        print " "


