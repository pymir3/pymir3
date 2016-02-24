import argparse
import numpy

import mir3.data.linear_decomposition as ld
import mir3.data.metadata as md
import mir3.module


class Elbow(mir3.module.Module):
    """Selects a binarization based on the elbow criterion.
    """

    def get_help(self):
        return """Selects a binarization using the elbow criterion"""

    def build_arguments(self, parser):
        parser.add_argument('infile', nargs='+',
                        help="""linear decomposition files""")

    def run(self, args):
        return self.find_best_elbow(args)


    def find_best_elbow(self, args):
        best_file_name = None
        best_elbow = -1.0
        this_elbow = 0
        th_list = []
        for filename in args.infile:
            with open(filename, 'rb') as handler:
                a = ld.LinearDecomposition().load(handler)
                # Stack periodicities for all instruments:
                full_data = None
                for k in a.data.right.keys():
                    if full_data is None:
                        full_data = a.data.right[k]
                    else:
                        full_data = numpy.vstack( (full_data,\
                            a.data.right[k]))

                frac = numpy.sum(full_data) /\
                        (full_data.shape[0] * full_data.shape[1])

                th_list.append( [frac, filename] )

        th_list.sort(key=lambda x: x[0])

        for i in xrange(len(th_list)-2):
            this_elbow = self.knee(th_list[i][0], th_list[i+1][0],\
                    th_list[i+2][0])

            if this_elbow > best_elbow:
                best_elbow = this_elbow
                best_file_name = th_list[i+3][1]


        print best_file_name

    def knee(self, a, b, c):
        return (c-b) - (b-a)

