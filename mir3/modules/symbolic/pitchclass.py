import argparse
import numpy

import mir3.data.score as score
import mir3.lib.mir.midifeatures as feats
import mir3.module

class Range(mir3.module.Module):
    """Calculates the pitch class histogram from a score"""

    def get_help(self):
        return """Pitch class histogram from a score. Prints the values on
    screen"""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""file containing score""")
        parser.add_argument('--normalize', action='store_true',
                            default=False, help="Normalize histogram to unit\
                            sum")
        parser.add_argument('--time', action='store_true',
                            default=False, help="Weight notes according to\
                            their duration")
    def run(self, args):
        s = score.Score().load(args.infile)
        histogram = feats.pitchclass_histogram(s.data, args.time)
        if args.normalize is True:
            histogram = histogram / numpy.sum(histogram)
        for i in xrange(12):
            print histogram[i],
        print " "




