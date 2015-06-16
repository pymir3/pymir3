import argparse
import numpy

import mir3.data.score as score
import mir3.lib.mir.midifeatures as feats
import mir3.module

class Rhythm(mir3.module.Module):
    """Calculates the rhythm histogram from a score"""

    def get_help(self):
        return """Rhythm histogram from a score. Prints the values on
    screen"""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('rb'),\
                help="""file containing score""")
        parser.add_argument('-r', '--resolution', default=25,\
                help="""Number of bins in the histogram""")

    def run(self, args):
        s = score.Score().load(args.infile)
        events = feats.event_list(s.data)
        histogram, lim = feats.rhythm_histogram(events, args.resolution)

        for i in xrange(args.resolution):
            print histogram[i],
        print " "




