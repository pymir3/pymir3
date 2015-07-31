import argparse
import numpy

import mir3.data.score as score
import mir3.lib.mir.midifeatures as feats
import mir3.module

class RelativeRange(mir3.module.Module):
    """Calculates relative range statistics from a score"""

    def get_help(self):
        return """Relative range statistics from a score. Prints the values on
    screen. Returns: maxRange, meanRange, standard_deviationRange"""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""file containing score""")
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
        (maxRange, meanRange, devRange) = feats.relative_range(events,\
                args.time_tolerance, args.duration)
        print maxRange, meanRange, devRange


