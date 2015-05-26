import argparse

import mir3.data.metadata as md
import mir3.data.note as note
import mir3.data.score as score
import mir3.module

class Label2Score(mir3.module.Module):
    """Converts a label text to a score.
    """

    def get_help(self):
        return """convert the 3 column text score to the internal
               representation"""

    def build_arguments(self, parser):
        parser.add_argument('-i','--instrument', help="""instrument associated
                            with the labels file provided""")

        parser.add_argument('infile', type=argparse.FileType('r'),
                            help="""labels file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""score file""")

    def run(self, args):
        s = self.convert(args.infile.readlines(),
                         args.instrument,
                         False)
        s.metadata.input = md.FileMetadata(args.infile)
        s.save(args.outfile)

    def convert(self, lines, instrument, save_metadata=True):
        """Converts from a list of strings to a score.

        Each string has 3 columns, that must be separable by split(). The
        columns provide the following information in order: onset, offset and
        pitch or name for the note.

        Args:
            lines: list of lines with 3 columns.
            instrument: name of an instrument.
            save_metadata: flag indicating whether the metadata should be
                           computed. Default: True.

        Returns:
            Score object.
        """
        # Converts the text into lists
        lines = [[str(v) for v in l.split()] for l in lines]

        notes = []
        for l in lines:
            onset = float(l[0])
            offset = float(l[1])

            # Checks if the line is valid. Discars invalid notes
            if onset > offset:
                continue

            # The last column may be pitch or note name. Tries as pitch and, in
            # case of a failure, tries as name.
            try:
                notes.append(note.Note(onset=onset, offset=offset,
                                       pitch=int(float(l[2]))))
            except ValueError, TypeError:
                notes.append(note.Note(onset=onset, offset=offset, name=l[2]))

        # Creates the score
        s = score.Score()
        s.metadata.instrument = instrument
        s.metadata.method_metadata = md.Metadata(type="label")
        if save_metadata:
            s.metadata.input = md.ObjectMetadata(lines)

        s.append(notes)

        return s
