import argparse
import numpy

import mir3.data.metadata as md
import mir3.data.spectrogram as spectrogram
import mir3.module

class TensorSpectrogram(mir3.module.Module):
    def get_help(self):
        return """calculates a tensor spectrogram fold from another
                    spectrogram file"""

    def build_arguments(self, parser):
        parser.add_argument('-f','--folds', type=int,
                            default=2, help="""number of folds
                            (default: %(default)s)""")

        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""original spectrogram file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""folded tensor spectrogram file""")

    def run(self, args):
        new_s = self.fold(spectrogram.Spectrogram().load(args.infile),
                          args.folds,
                          True)
        new_s.save(args.outfile)

    def fold(self, s, folds=2, save_metadata=True):
        """Cuts some pieces of the spectrogram.

        Keeps only a desired rectangle in the frequency/time matrix
        associated with the spectrogram. By default, all arguments not
        provided don't cause any restriction on the trimmed region.

        Args:
            folds: number of folds (tensor depth)
            save_metadata: flag indicating whether the metadata should be
                           computed. Default: True.

        Returns:
            Trimmed Spectrogram object.
        """

        #print min_time, max_time, min_freq, max_freq
        new_s = spectrogram.Spectrogram()
        new_s.data = s.data[:,0:-folds]

        nFolds = 1
        while nFolds < folds:
            new_s.data = numpy.vstack( (new_s.data,
                s.data[:,nFolds:-folds+nFolds]) )
            nFolds += 1

        new_s.metadata.min_freq = s.metadata.min_freq
        new_s.metadata.min_time = s.metadata.min_time
        new_s.metadata.max_freq = s.metadata.max_freq * folds
        new_s.metadata.max_time = s.metadata.max_time
        new_s.metadata.sampling_configuration = \
            s.metadata.sampling_configuration
        new_s.metadata.method = md.Metadata(original_input=s.metadata.input,
                                            original_method=s.metadata.method,
                                            name='tensor-fold',
                                            min_freq=s.metadata.min_freq,
                                            max_freq=s.metadata.max_freq*folds,
                                            min_time=s.metadata.min_time,
                                            max_time=s.metadata.max_time)
        if save_metadata:
            s.metadata.input = md.ObjectMetadata(s)

        return new_s
