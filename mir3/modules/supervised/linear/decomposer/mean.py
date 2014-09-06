import argparse
import numpy

import mir3.data.linear_decomposition as ld
import mir3.data.metadata as md
import mir3.data.spectrogram as spectrogram
import mir3.module

class Mean(mir3.module.Module):
    def get_help(self):
        return """use the mean of a part of the note's spectrogram as basis"""

    def build_arguments(self, parser):
        parser.add_argument('-f','--number-frames', default=10, type=int,
                            help="""maximum number of frames that will be used
                            (default: %(default)s)""")
        parser.add_argument('-s','--frame-skip', default=2, type=int,
                            help="""frames that will be skipped after the
                            detected attack (default: %(default)s)""")

        parser.add_argument('instrument', help="""name of the instrument that
                            created the spectrogram""")
        parser.add_argument('note', help="""name of the note that created the
                            spectrogram""")

        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""spectrogram file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""basis file""")

    def run(self, args):
        d = self.compute(spectrogram.Spectrogram().load(args.infile),
                         args.note,
                         args.instrument,
                         args.number_frames,
                         args.frame_skip,
                         False)

        d.metadata.left[(args.instrument, args.note)].spectrogram_input = \
                md.FileMetadata(args.infile)

        d.save(args.outfile)

    def compute(self, s, note, instrument, number_frames=10, frame_skip=2,
                save_metadata=True):
        """Builds a basis from the mean of a spectrogram.

        Uses a part of the spectrogram to compute the mean value.

        Args:
            s: Spectrogram object.
            note: note's name.
            instrument: instrument's name.
            number_frames: number of frames to use. Default: 10.
            frame_skip: number of frames to skip after the attack. Default: 2.
            save_metadata: flag indicating whether the metadata should be
                           computed. Default: True.

        Returns:
            LinearDecomposition object with the window's mean on the left.
        """
        data = s.data

        # Detects attack
        energy = numpy.sum(data,0)
        energy_peak = numpy.argmax(energy)

        # Max number of frames availables
        max_frames = numpy.size(data,1)

        # Avoids getting less frames because data ended
        if energy_peak > (max_frames - number_frames - frame_skip - 1):
            energy_peak = max_frames - number_frames - frame_skip - 1

        # But if there's enough data, skip a few frames after energy peak
        else:
            energy_peak += frame_skip

        # Cuts data
        data = data[:,energy_peak:energy_peak+number_frames]

        # Computes the mean
        data = numpy.array([numpy.mean(data,1)]).transpose()

        # Saves metadata
        input_metadata = md.ObjectMetadata(s) if save_metadata else None

        # Stores the basis as a decompositon
        d = ld.LinearDecomposition()
        d.add((instrument, note),
              left=data,
              left_metadata=md.Metadata(method='mean',
                                        number_of_frames=number_frames,
                                        frame_skip=frame_skip,
                                        spectrogram=s.metadata,
                                        spectrogram_input=input_metadata))

        return d
