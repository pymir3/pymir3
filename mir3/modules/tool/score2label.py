import argparse

import mir3.data.score as score
import mir3.module

class Score2Label(mir3.module.Module):
    def get_help(self):
        return """convert the internal score representation to the 3 column
               text"""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('rb'), help="""score
                            file""")
        parser.add_argument('outfile', type=argparse.FileType('w'),
                            help="""labels file""")

    def run(self, args):
        args.outfile.writelines(self.convert(score.Score().load(args.infile)))

    def convert(self, s):
        """Converts a score to a list of strings.

        Each string has 3 columns, and are separable by split(). The columns
        provide the following information in order: onset, offset and pitch or
        name for the note.

        Args:
            s: Score object.

        Returns:
            List of strings.
        """
        lines = []
        for n in sorted(s.data):
            lines.append('   %.7e   %.7e   %.7e\n' % (n.data.onset,
                         n.data.offset, n.data.pitch))

        return lines
