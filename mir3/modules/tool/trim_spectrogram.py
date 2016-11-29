import argparse

import mir3.data.metadata as md
import mir3.data.spectrogram as spectrogram
import mir3.module
import copy

class TrimSpectrogram(mir3.module.Module):
    def get_help(self):
        return """trim a spectrogram file"""

    def build_arguments(self, parser):
        parser.add_argument('-f','--minimum-frequency', type=float, default=0.,
                            help="""minimum frequency to keep (default:
                            %(default)s)""")
        parser.add_argument('-F','--maximum-frequency', type=float,
                            default=float('inf'), help="""maximum frequency to
                            keep""")
        parser.add_argument('-t','--minimum-time', type=float, default=0.,
                            help="""minimum time to keep (default:
                            %(default)s)""")
        parser.add_argument('-T','--maximum-time', type=float,
                            default=float('inf'), help="""maximum time to keep
                            (default: %(default)s)""")

        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""original spectrogram file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""trimmed spectrogram file""")

    def run(self, args):
        new_s = self.trim(spectrogram.Spectrogram().load(args.infile),
                          args.minimum_frequency, args.maximum_frequency,
                          args.minimum_time, args.maximum_time,
                          False)
        new_s.metadata.input = md.FileMetadata(args.infile)
        new_s.save(args.outfile)

    def trim(self, s, min_freq=0, max_freq=float('Inf'), min_time=0,
             max_time=float('Inf'), save_metadata=True):
        """Cuts some pieces of the spectrogram.

        Keeps only a desired rectangle in the frequency/time matrix
        associated with the spectrogram. By default, all arguments not
        provided don't cause any restriction on the trimmed region.

        Args:
            min_freq: minimum frequency to be kept. Default: 0.
            max_freq: maximum frequency to be kept. Default: inf.
            min_time: minimum time to be kept. Default: 0.
            max_time: maximum time to be kept. Default: inf.
            save_metadata: flag indicating whether the metadata should be
                           computed. Default: True.

        Returns:
            Trimmed Spectrogram object.
        """
        # Regard default parameters
        if max_freq > s.metadata.max_freq:
            max_freq = s.metadata.max_freq

        if max_time > s.metadata.max_time:
            max_time = s.metadata.max_time

        # Finds frequency and time bounds
        maxK = s.freq_bin(max_freq)
        minK = s.freq_bin(min_freq)
        maxT = s.time_bin(max_time)
        minT = s.time_bin(min_time)

        #print min_time, max_time, min_freq, max_freq

        new_s = spectrogram.Spectrogram()
        new_s.data = s.data[minK:maxK+1, minT:maxT+1]
        new_s.metadata.min_freq = s.freq_range(minK)[0]
        new_s.metadata.min_time = s.time_range(minT)[0]
        new_s.metadata.max_freq = s.freq_range(maxK)[0]
        new_s.metadata.max_time = s.time_range(maxT)[0]
        new_s.metadata.sampling_configuration = \
            s.metadata.sampling_configuration
        new_s.metadata.input_metadata = copy.deepcopy(s.metadata)

        new_s.metadata.method = md.Metadata(original_input=s.metadata.input,
                                            original_method=s.metadata.method,
                                            name='trim',
                                            min_freq=min_freq,
                                            max_freq=max_freq,
                                            min_time=min_time,
                                            max_time=max_time)
        if save_metadata:
            new_s.metadata.input = md.ObjectMetadata(s)

        return new_s
