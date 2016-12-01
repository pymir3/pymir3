import argparse
import numpy
import scipy.io.wavfile
import mir3.data.feature_track as track
import mir3.data.spectrogram as spectrogram
import mir3.lib.mir.features as feats
import mir3.lib.mir.tdom_features as td_feats
import mir3.module

class TDZeroCrossings(mir3.module.Module):
    """Calculate Time Domain Zero Crossings from wav file"""

    def get_help(self):
        return """Time Domain Zero Crossings for each analysis window of a wav file"""

    def build_arguments(self, parser):
        parser.add_argument('-F','--frame-length', type=int, default=1024, help="""size of frames, in samples (default: %(default)s)""")
        parser.add_argument('-W','--window-size', type=int, default=512, help="""sliding window size, in samples (default: %(default)s)""")
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""wav audio file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""output track file""")

    def calc_track(self, data, frame_length, window_size, rate=44100):
        t = track.FeatureTrack()
        t.data = td_feats.zero_crossings(data, frame_length, window_size)
        t.metadata.sampling_configuration.fs = rate
        t.metadata.sampling_configuration.ofs = rate / window_size
        t.metadata.sampling_configuration.window_length = frame_length
        t.metadata.feature = "TDZeroCrossings"
        return t

    def run(self, args):
        t = self.calc_track(args.infile, args.frame_length, args.window_size)
        t.metadata.filename = infile
        t.save(args.outfile)

