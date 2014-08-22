import argparse
import mir3.data.feature_track as track
import mir3.module
import numpy

class Stack(troll.module.Module):
    def get_help(self):
        return """Joins two or more feature tracks into one multi-dimensional feature track"""

    def build_arguments(self, parser):
        parser.add_argument('input', nargs='+', type=argparse.FileType('r'),
                            help="""input track files""")
        parser.add_argument('output', type=argparse.FileType('w'), help="""track
                            file""")

    def run(self, args):
        o = None
        
        t = track.FeatureTrack()
        for a in args.input:
            if o is None:
                o = track.FeatureTrack()
                o.load(a)
                if o.data.ndim == 1:
                    o.data.shape = (o.data.size,1)
            else:
                t.load(a)
                if t.data.ndim == 1:
                    t.data.shape = (t.data.size,1)
                o.data = numpy.hstack( (o.data, t.data) )
                o.metadata.feature = o.metadata.feature + \
                    " " + t.metadata.feature

        o.save(args.output)
