import argparse
import numpy

import mir3.data.linear_decomposition as ld
import mir3.data.metadata as md
import mir3.lib.periodicity as per
import mir3.module


class BestPeriodicity(mir3.module.Module):
    """Binarizes a linear decomposition using a threshold.
    """

    def get_help(self):
        return """Finds the periodicity of a series of binarizations received as
                    inputs"""

    def build_arguments(self, parser):
        parser.add_argument('-e', '--exponent', type=float, default=2.0,\
                        help="""Exponent for the periodicity""")
        parser.add_argument('infile', nargs='+',
                        help="""linear decomposition files""")

    def run(self, args):
        return self.find_best_periodicity(args)

    def find_best_periodicity(self, args):
        best_file_name = None
        best_periodicity = -1.0
        this_periodicity = 0.0
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

                this_periodicity = per.periodicity(full_data, e=args.exponent)
                if this_periodicity > best_periodicity:
                    best_periodicity = this_periodicity
                    best_file_name = filename

        print best_file_name

