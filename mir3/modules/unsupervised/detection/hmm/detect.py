import argparse
import numpy

import mir3.data.linear_decomposition as ld
import mir3.data.metadata as md
import mir3.module
import mir3.lib.ml.viterbi as vit


class Detect(mir3.module.Module):
    """Binarizes a linear decomposition using a Hidden Markov Model.
    """

    def get_help(self):
        return """binarize the linear decomposition activation using an HMM"""

    def build_arguments(self, parser):
        parser.add_argument('threshold', type=float, help="""threshold used to
                            binarize""")
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""linear decomposition file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""binarized linear decomposition file""")

    def run(self, args):
        d = self.binarize(ld.LinearDecomposition().load(args.infile),
                          args.threshold,
                          False)
        meta = md.FileMetadata(args.infile)
        for k, data, metadata in d.right():
            metadata.activation_input = meta
        d.save(args.outfile)

    def binarize(self, d, threshold, save_metadata=True):
        """Alters the given linear decomposition, binarizing it.

        The resulting linear decomposition has binary values, where positions
        are True if the value was higher than the threshold.

        The argument provided is destroyed.

        Args:
            d: LinearDecomposition object to binarize.
            threshold: activation limit for it to become True.
            save_metadata: flag indicating whether the metadata should be
                           computed. Default: True.

        Returns:
            Same decomposition given in arguments.
        """
        if save_metadata:
            metadata = md.ObjectMetadata(a)
        else:
            metadata = None

        meta = md.Metadata(name="threshold-viterbi",
                           threshold=threshold,
                           activation_input=metadata,
                           original_method=None)

        # Binarizes the data and adjusts the metadata
        for k in d.data.right.keys():

            # Separate high-value and low-value samples
            (lin, col) = d.data.right[k].shape
            pos_samples = []
            neg_samples = []
            for x in xrange(lin):
                for y in xrange(col):
                    if d.data.right[k][x,y] >= threhsold:
                        pos_samples.append(d.data.right[k][x,y])
                    else:
                        neg_samples.append(d.data.right[k][x,y])

            # Prepare for viterbi decoding
            states = ('A', 'S')

            start_probability = {'A': -9000, 'S': 0.0}
            transition_probability = {
                   'A' : {'A': 0.9, 'S': 0.1},
                   'S' : {'A': 0.1, 'S': 0.9}
                   }

            emission_probability = {
               'A' : [numpy.mean(pos_samples), numpy.var(pos_samples)],
               'S' : [numpy.mean(neg_samples), numpy.var(neg_samples)]
               }

            # Viterbi decoding in each line of the activation matrix
            for x in xrange(lin):
                (p, o) = vit.viterbi(d.data.right[k][x,:], states,\
                   start_probability, transition_probability,\
                   emission_probability)
                d.data.right[k][x,:] = numpy.array(o) == 'A'

            d.metadata.right[k] = md.Metadata(method="threshold-viterbi",
                                              threshold=threshold,
                                              activation_input=metadata,
                                              original_method =
                                                d.metadata.right[k])

        return d

