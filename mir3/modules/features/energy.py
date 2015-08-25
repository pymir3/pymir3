import argparse
import numpy

import mir3.data.feature_track as track
import mir3.data.spectrogram as spectrogram
import mir3.lib.mir.features as feats
import mir3.module

class Energy(mir3.module.Module):
    """Calculates the energy track from a spectrogram"""

    def get_help(self):
        return """Energy of each frame of a spectrogram"""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""file containing spectrogram""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""output track file""")

    def run(self, args):
        s = spectrogram.Spectrogram().load(args.infile)

        #print s.data.shape

        t = track.FeatureTrack()
        t.data = feats.energy(s.data/ \
            s.metadata.sampling_configuration.dft_length)

        #print t.data.shape

        t.metadata.sampling_configuration = s.metadata.sampling_configuration
        t.metadata.feature = "Energy"
        t.metadata.filename = s.metadata.input.name
        t.save(args.outfile)

