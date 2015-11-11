import argparse

import mir3.data.linear_decomposition as ld
import mir3.data.metadata as md
import mir3.module

import numpy

class HardSparsity(mir3.module.Module):
    """Applies hard sparsity constrain on a linear decomposition.
    """

    def get_help(self):
        return """applies hard sparsity constrain on a linear decomposition"""

    def build_arguments(self, parser):
        parser.add_argument('sparsity', type=int, help="""maximum polyphony""")
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""input linear decomposition file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""output linear decomposition file""")

    def run(self, args):
        d = self.hard_sparsity(ld.LinearDecomposition().load(args.infile),
                          args.sparsity,
                          False)
        meta = md.FileMetadata(args.infile)
        for k, data, metadata in d.right():
            metadata.activation_input = meta
        d.save(args.outfile)

    def hard_sparsity(self, d, sparsity, save_metadata=True):
        """Alters the given linear decomposition, applying a median filter.

        The filtering process is done in the time domain.

        The argument provided is destroyed.

        Args:
            d: LinearDecomposition object to filter.
            sparsity: maximum polyphony allowed.
            save_metadata: flag indicating whether the metadata should be
                           computed. Default: True.

        Returns:
            Same decomposition given in arguments.
        """
        if save_metadata:
            metadata = md.ObjectMetadata(a)
        else:
            metadata = None

        meta = md.Metadata(name="sparsity_level",
                           sparsity=sparsity,
                           activation_input=metadata,
                           original_method=None)

        # Binarizes the data and adjusts the metadata
        A = None
        p = []
        for k in d.data.right.keys():
            if A is None:
                A = d.data.right[k]
            else:
                A = numpy.vstack((A, d.data.right[k]))
            p.append(k)

        for i in xrange(A.shape[1]):
            b = numpy.partition(A[:,i], sparsity-1)[sparsity-1]
            A[:,i] = A[:,i] * (A[:,i] >= b)


        for argk in xrange(len(p)):
            d.data.right[p[argk]] = A[argk,:]
            d.data.right[p[argk]].shape = (1, len(d.data.right[p[argk]]))
            d.metadata.right[p[argk]] = md.Metadata(method="sparsity_level",
                                              sparsity=sparsity,
                                              activation_input=metadata,
                                              original_method =
                                                d.metadata.right[k])

        return d

