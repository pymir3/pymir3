import argparse
import numpy

import mir3.data.linear_decomposition as ld
import mir3.module

class Variance(mir3.module.Module):
    def get_help(self):
        return """make activations for each basis have unitary covariance"""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""spectrogram file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""basis file""")

    def run(self, args):
        d = self.compute(ld.LinearDecomposition().load(args.infile))
        d.save(args.outfile)

    def compute(self, d):
        """Normalizes the activation variance.

        For each basis, finds the covariance considering all activations
        associated with it and normalizes The product still holds the same
        value. The decomposition provided is changed by this function.

        Args:
            d: LinearDecomposition object

        Returns:
            LinearDecomposition given in argument.
        """
        # Iterates for each basis
        for left_k, left_data, left_metadata in d.left():
            len_left_k = len(left_k)

            # Finds the associated activations
            right_k = [right_k for right_k in d.data.right.keys()
                               if right_k[0:len_left_k] == left_k]

            # Gets standard deviation
            right_values = numpy.hstack([d.data.right[k].reshape(-1)
                                         for k in right_k])
            right_std = numpy.sqrt(numpy.cov(right_values));
            scale = 1./right_std

            # Normalizes
            left_data /= scale

            for k in right_k:
                d.data.right[k] *= scale

        return d
