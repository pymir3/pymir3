import argparse
import numpy

import mir3.data.score as score
import mir3.lib.mir.midifeatures as feats
import mir3.module

class Density(mir3.module.Module):
    """Calculates the note density statistics from a score"""

    def get_help(self):
        return """Note range from a score. Prints the average, standard
        deviation, minimum and maximum notes on the screen"""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""file containing score""")

    def run(self, args):
        s = score.Score().load(args.infile)
        events = feats.event_list(s.data)
        (dMean, dDev, dMin, dMax) = feats.note_density(events)
        print dMean, dDev, dMin, dMax



