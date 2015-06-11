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
        parser.add_argument('infile', type=argparse.FileType('rb'),\
                help="""file containing score""")
        parser.add_argument('-d', '--duration', default=False,\
                action='store_true', help="""Use duration as weights for the\
                histogram""")

    def run(self, args):
        s = score.Score().load(args.infile)
        histogram = feats.pitchclass_histogram(s.data, args.duration)
        for i in xrange(12):
            print histogram[i],
        print " "




