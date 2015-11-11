import argparse
import numpy

import mir3.data.score as sc
import mir3.data.metadata as md
import mir3.lib.mir.midifeatures as feats
import mir3.module


class BestNoteDistribution(mir3.module.Module):
    """Selects the score with the best note distribution
    """

    def get_help(self):
        return """Finds the periodicity of a series of binarizations received as
                    inputs"""

    def build_arguments(self, parser):
        parser.add_argument('-e', '--exponent', type=float, default=2.0,\
                        help="""Exponent for the periodicity""")
        parser.add_argument('infile', nargs='+',
                        help="""score files""")

    def run(self, args):
        return self.find_best_note_distribution(args)

    def find_best_note_distribution(self, args):
        best_file_name = None
        best_score = 9000000000
        for filename in args.infile:
            if best_file_name is None: # Avoids returning empty values
                best_file_name = filename

            with open(filename, 'rb') as handler:
                a = sc.Score().load(handler)
                event_list = feats.event_list(a.data)
                if len(event_list) > 0: # Avoids empty scores
                    (max_range, mean_range, std_range) = \
                        feats.relative_range(event_list)
                    if max_range < best_score:
                        best_score = max_range
                        best_file_name = filename


        print best_file_name

