import argparse
import numpy

import mir3.data.feature_track as track
import mir3.data.spectrogram as spectrogram
import mir3.module

class Identity(mir3.module.Module):
    """Generates a feature track that is equal to a spectrogram"""

    def get_help(self):
        return """Each feature frame is equal to a frame of a spectrogram"""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""file containing spectrogram""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""output track file""")

    def run(self, args):
        s = spectrogram.Spectrogram().load(args.infile)

        t = track.FeatureTrack()
        t.data = s.data.T

        t.metadata.sampling_configuration = s.metadata.sampling_configuration
        t.metadata.feature = ""
        for f in xrange(s.data.shape[0]):
            t.metadata.feature += "DFT_" + str(s.freq_bin(f)) + "Hz "

        t.metadata.filename = s.metadata.input.name
        t.save(args.outfile)

