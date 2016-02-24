import argparse
import numpy

import mir3.data.score as score
import mir3.lib.mir.midifeatures as feats
import mir3.module

class Range(mir3.module.Module):
    """Calculates the note range from a score"""

    def get_help(self):
        return """Note range from a score. Prints the minimum and maximum notes
    on the screen"""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""file containing score""")

    def run(self, args):
        s = score.Score().load(args.infile)
        (min_note, max_note) = feats.range(s.data)
        print min_note, max_note



