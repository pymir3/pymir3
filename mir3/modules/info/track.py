import argparse
import mir3.data.feature_track as track
import mir3.module
import numpy

class Track(mir3.module.Module):
    def get_help(self):
        return """outputs a matrix in ASCII for the track"""

    def build_arguments(self, parser):
        parser.add_argument('-f', '--filename', action='store_true', default=False,
                            help="""display only the filename of the original source (default:
                            %(default)s)""")
        parser.add_argument('-t','--time', action='store_true', default=False,
                            help="""output samplewise time signature (default:
                            %(default)s)""")
        parser.add_argument('-n','--norm', action='store_true', default=False,
                            help="""normalize track to zero mean and unit
                            variance (default: %(default)s)""")
        parser.add_argument('infile', type=argparse.FileType('r'), help="""track
                            file""")

    def run(self, args):
        a = track.FeatureTrack().load(args.infile)
        t = 0

        if args.filename is True:
            print "Stored ", len(a.metadata.filename), " files"
            print a.metadata.filename
            exit()
        
        b = a.data

        if b.ndim == 1:
            b.shape = (b.size,1)

        if args.norm:
            b = (b - b.mean(axis=0))/numpy.maximum(0.00001, b.std(axis=0))
        
        for n in xrange(b.shape[0]):
            # TODO: update to use metadata
            if args.time:
                print t,
                t += (1.0/a.metadata.sampling_configuration.ofs)
            for k in xrange(b.shape[1]):
                print b[n,k],
            print ""

        print b.shape
        print a.metadata.feature
        