import argparse
import numpy
import copy

import mir3.data.feature_track as track
import mir3.module

class Join(mir3.module.Module):
    def get_help(self):
        return """Joins two or more feature tracks into one multi-dimensional
        feature track"""

    def build_arguments(self, parser):
        parser.add_argument('input', nargs='+', type=argparse.FileType('rb'),
                            help="""input track files""")
        parser.add_argument('output', type=argparse.FileType('wb'),
                            help="""track file""")

    def join(self, feature_tracks):
        data = []
        features = []

        o = track.FeatureTrack()
        o.metadata.input_metadata = []

        for t in feature_tracks:
            if t is None:
                continue

            if t.data.ndim == 1:
                t.data.shape = (t.data.size,1)
            data.append(t.data)
            features.append(t.metadata.feature)
            o.metadata.input_metadata.append(copy.deepcopy(t.metadata))
            #print a.name, t.metadata.feature, t.data.shape

        o.data = numpy.hstack(data)
        o.metadata.feature = ' '.join(features)
        o.metadata.filename = t.metadata.filename
        o.metadata.sampling_configuration = t.metadata.sampling_configuration


        return o

    def run(self, args):
        print "Joining features"
        features = []

        for a in args.input:
            t = track.FeatureTrack()
            t = t.load(a)
            features.append(t)
            print a.name, t.metadata.feature, t.data.shape

        o = self.join(features)

        o.save(args.output)
