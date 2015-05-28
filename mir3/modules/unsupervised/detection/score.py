import argparse

import mir3.data.linear_decomposition as ld
import mir3.data.metadata as md
import mir3.data.note as note
import mir3.data.score as score
import mir3.module

class Score(mir3.module.Module):
    """Converts a linear decomposition with binary activation to a score.
    """

    def get_help(self):
        return """use a linear decomposition to create a score"""

    def build_arguments(self, parser):
        parser.add_argument('-f','--frequency', type=float, default=0.,
                            help="""sampling frequency to consider (default: use
                            the piece spectrogram frequency)""")
        parser.add_argument('-l','--minimum-length', type=float, default=0.,
                            help="""minimum note length (default:
                            %(default)s)""")

        parser.add_argument('instrument', help="""instrument whose score will be
                            extracted""")
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""linear decomposition file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""score file""")

    def run(self, args):
        s = self.convert(ld.LinearDecomposition().load(args.infile),
                         args.instrument,
                         args.frequency,
                         args.minimum_length,
                         False)
        s.metadata.input = md.FileMetadata(args.infile)
        s.save(args.outfile)

    def convert(self, d, instrument, frequency, minimum_length,
                save_metadata=True):
        """Converts an linear decomposition to a score.

        If the given frequency is 0, then the frequency becomes the one in the
        spectrogram used to compute the linear decomposition activation.

        Args:
            a: LinearDecomposition object with binary right side.
            instrument: name of the instrument to be extracted.
            frequency: frequency used to transfer activation time bins to
                       timestamps.
            minimum_length: minimum length of note to be considered.
            save_metadata: flag indicating whether the metadata should be
                           computed. Default: True.

        Returns:
            Score object.
        """
        # Loads valid frequency to be used
        if frequency == 0.:
            ofs = d.metadata.get('sampling_configuration.ofs')
        else:
            ofs = float(frequency)

        s = score.Score()

        s.metadata.instrument = instrument
        if save_metadata:
            s.metadata.input = md.ObjectMetadata(d)

        s.metadata.method_metadata = \
                md.Metadata(type='algorithm',
                            algorithm='binary activation',
                            frequency=ofs,
                            minimum_length=minimum_length,
                            activation_metadata=d.metadata.right)

        # TODO: check if this parameter really does what it's supposed to.
        # Currently it ignores zeros in the activation matrix once a not has
        # been detected and the minimum window haven't been found.
        minimum_window = minimum_length * ofs

        for k, data, metadata in d.right():
            if k[0] != instrument:
                continue

            note_start = -1
            activation = data

            # Considers only one line per note for now. TODO: consider more
            for t in range(activation.shape[1]):
                # Checks if starting a new note
                if activation[0,t] and note_start == -1:
                    note_start = t

                # Checks for note ending
                elif not activation[0,t] and note_start != -1:
                    # If minum length is met, adds note
                    if t-note_start > minimum_window:
                        s.append(note.Note(onset=note_start/float(ofs),\
                            offset=t/float(ofs), name=k[1]))
                    # Marks note as finished
                    note_start = -1

        return s
