import numpy
import argparse
import mir3.data.spectrogram as spectrogram
import mir3.data.feature_track as track
import mir3.lib.mir.features as feats
import mir3.module

class Energy(mir3.module.Module):
    """Calculates the spectral rolloff track from a spectrogram"""

    def get_help(self):
        return """Rolloff of each frame of a spectrogram"""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('r'),
                            help="""file containing spectrogram""")
        parser.add_argument('outfile', type=argparse.FileType('w'),
                            help="""output track file""")

    def run(self, args):
        s = spectrogram.Spectrogram().load(args.infile)

        t = track.FeatureTrack()
        t.data = feats.rolloff(s.data) * \
            s.metadata.sampling_configuration.ofs

        t.metadata.sampling_configuration = s.metadata.sampling_configuration
        t.metadata.feature = "Roll-Off"
        t.metadata.filename = s.metadata.input.name
        t.save(args.outfile)


