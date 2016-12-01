import argparse
import numpy
import copy

import mir3.data.feature_track as track
import mir3.data.spectrogram as spectrogram
import mir3.lib.mir.mfcc as feats
import mir3.module

class Mfcc(mir3.module.Module):
    """Calculates the MFCC track from a spectrogram"""

    def get_help(self):
        return """Spectral flow of each frame of a spectrogram"""

    def build_arguments(self, parser):
        parser.add_argument('-n','--number', type=int, default=18,
                            help="""number of mfccs to calculate (default:
                            %(default)s)""")
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""file containing spectrogram""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""output track file""")


    def calc_track(self, s, n=20):
        t = track.FeatureTrack()
        t.data = feats.mfcc(s, n)

        t.metadata.sampling_configuration = s.metadata.sampling_configuration
        feature = ""
        for i in range(n):
            feature = feature + "MFCC_"+ str(i) + " "
        t.metadata.feature = feature
        t.metadata.filename = s.metadata.input.name
        t.metadata.input_metadata = copy.deepcopy(s.metadata)

        return t

    def run(self, args):
        s = spectrogram.Spectrogram().load(args.infile)
        t = self.calc_track(s, args.number)
        t.save(args.outfile)

