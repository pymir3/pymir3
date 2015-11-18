import argparse
import numpy

import mir3.module
import mir3.data.linear_decomposition as ld
import matplotlib.pyplot as plt

class ActivationHistogram(mir3.module.Module):
    """Gathers a data histogram for a structure.

    This is a major hack inside the data structure and should be treated
    carefully.
    """

    def get_help(self):
        return """returns histogram of an activation matrix"""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""object file""")
        parser.add_argument('-bins', '-b', type=int, default=10,
                            help="""number of histogram bins. Default = 10""")

        parser.add_argument('-threshold', '-t', type=float, default=0.01,
                            help="""Threshold for silence. Default = 0.01""")



    def run(self, args):
        # Gets the name of the class stored in the file
        a = ld.LinearDecomposition().load(args.infile)

        # Merges decompositions
        #print a.data.right[('piano', 'A3', 0)]

        X = numpy.vstack([a.data.right[x] for x in a.data.right.keys()])

        X.shape = (X.shape[0] * X.shape[1], )
        X = numpy.array([X[i] for i in xrange(X.shape[0]) if X[i] >\
            args.threshold])


        # Creates an instace using the read class name
        n, bins, patches = plt.hist(X, args.bins, normed = 1)
        n = numpy.array(n)
        if numpy.sum(n) > 0:
            n = n / float(numpy.sum(n))

        for k in xrange(len(n)):
            print bins[k], n[k]
