import argparse
import numpy

import mir3.data.feature_track as track
import mir3.data.spectrogram as spectrogram
import mir3.module

class FilterBank(mir3.module.Module):
    """Calculates energy through a triangular filter bank"""

    def get_help(self):
        return """Bandwise energy of each frame of a spectrogram"""

    def build_arguments(self, parser):
        parser.add_argument('central_frequencies', type=float,
                help="""central filter frequencies""", nargs="+")
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""file containing spectrogram""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""output track file""")

    def build_filterbank(self, freqs, s):
        """Builds a filterbank as a numpy array

        freqs = list of central frequenceis
        s = spectrogram
        """
        a = [0]
        a += freqs
        a += [s.metadata.max_freq]

        H = numpy.zeros( (len(freqs), s.data.shape[0]) )

        for f in xrange(len(freqs)):
            k_min = numpy.ceil(s.freq_bin(a[f]))
            k_c = round(s.freq_bin(a[f+1]))
            k_max = numpy.floor(s.freq_bin(a[f+2]))
            H[f, k_min:k_c] = numpy.linspace(0, 1, k_c-k_min)
            H[f, k_c-1:k_max-1] = numpy.linspace(1, 0, k_max-k_c)

        return H

    def run(self, args):
        s = spectrogram.Spectrogram().load(args.infile)

        t = track.FeatureTrack()

        H = self.build_filterbank(args.central_frequencies, s)


        t.data = numpy.dot(H, s.data).T

        t.metadata.sampling_configuration = s.metadata.sampling_configuration
        t.metadata.feature = ""
        for f in args.central_frequencies:
            t.metadata.feature += "FB_" + str(f) + "Hz "

        t.metadata.filename = s.metadata.input.name
        t.save(args.outfile)

