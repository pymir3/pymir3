import argparse
import mir3.data.feature_track as track
import mir3.module
import numpy

class Join(mir3.module.Module):
    def get_help(self):
        return """Joins two or more feature tracks into one multi-dimensional
        feature track"""

    def build_arguments(self, parser):
        parser.add_argument('input', nargs='+', type=argparse.FileType('r'),
                            help="""input track files""")
        parser.add_argument('output', type=argparse.FileType('w'), help="""track
                            file""")

    def run(self, args):
        data = []
        features = []

        t = track.FeatureTrack()
        for a in args.input:
            t = t.load(a)
            if t.data.ndim == 1:
                t.data.shape = (t.data.size,1)
            data.append(t.data)
            features.append(t.metadata.feature)

        o = track.FeatureTrack()
        o.data = numpy.hstack(data)
        o.metadata.feature = ' '.join(features)

        o.save(args.output)
