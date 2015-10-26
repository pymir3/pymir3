import argparse
import numpy
import scipy.io.wavfile
import mir3.data.feature_track as track
import mir3.data.spectrogram as spectrogram
import mir3.lib.mir.features as feats
import mir3.lib.mir.tdom_features as td_feats
import mir3.module

class LowEnergy(mir3.module.Module):
    """Calculate the Low Energy feature"""

    def get_help(self):
        return """Low energy feature for each texture window of a spectrogram"""

    def build_arguments(self, parser):
        parser.add_argument('-A','--texture-length', type=int, default=40, help="""size of texture window, in analysis windows (frames) (default: %(default)s)""")
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""spectrogram file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""output track file""")

    def run(self, args):
        
        s = spectrogram.Spectrogram().load(args.infile)

        #print s.data.shape

        t = track.FeatureTrack()
        t.data = feats.low_energy(s.data/s.metadata.sampling_configuration.dft_length, args.texture_length)

        t.metadata.sampling_configuration = s.metadata.sampling_configuration
        t.metadata.feature = "LowEnergy"
        t.metadata.filename = s.metadata.input.name
        t.save(args.outfile)

