import argparse
import copy
import hmmlearn.hmm as hmm
import numpy

import mir3.data.linear_decomposition as ld
import mir3.data.metadata as md
import mir3.module

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

        meta = md.Metadata(name="hmm",
                           threshold=threshold,
                           activation_input=metadata,
                           original_method=None)

        # Trains HMM on full matrix
        A = []
        for k in d.data.right.keys():
            J = d.data.right[k].transpose()
            Jdiff = numpy.diff(J, axis=0)
            A.append(numpy.hstack((J[:-1,], Jdiff)))

        mu = 1.0
        sigma = 2.0
        init_mean = numpy.array([[mu-sigma, mu+sigma], [mu-sigma, mu+sigma]])
        init_transition = numpy.array([ [0.5, 0.5], [0.5, 0.5] ])
        init_covar = numpy.array( [[sigma, sigma],[sigma, sigma]] )
        start_prob = numpy.array( [1.0, 0.0] )

        model = hmm.GaussianHMM(n_components=2, covariance_type='full',\
                startprob=start_prob, transmat=init_transition)
        model.mean_ = init_mean
        model.covar_ = init_covar

        model.fit(A)

        # Binarizes the data and adjusts the metadata
        for k in d.data.right.keys():
            J = d.data.right[k].transpose()
            Jdiff = numpy.diff(J, axis=0)
            Jfull = numpy.hstack((J[1:,], Jdiff))

            prob, x = model.decode(Jfull)
            x.shape = (1, d.data.right[k].shape[1]-1)

            x = numpy.hstack( (numpy.array([[0]]), x) )
            d.data.right[k] = x

            d.metadata.right[k] = md.Metadata(method="hmm",
                                              threshold=threshold,
                                              activation_input=metadata,
                                              original_method =
                                                d.metadata.right[k])

        return d

