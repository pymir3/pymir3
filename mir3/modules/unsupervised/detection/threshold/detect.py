import argparse

import mir3.data.linear_decomposition as ld
import mir3.data.metadata as md
import mir3.module

class Detect(mir3.module.Module):
    """Binarizes a linear decomposition using a threshold.
    """

    def get_help(self):
        return """binarize the linear decomposition activation using a given
               threshold"""

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

        meta = md.Metadata(name="threshold",
                           threshold=threshold,
                           activation_input=metadata,
                           original_method=None)

        # Binarizes the data and adjusts the metadata
        for k in d.data.right.keys():
            d.data.right[k] = (d.data.right[k] >= threshold)
            d.metadata.right[k] = md.Metadata(method="threshold",
                                              threshold=threshold,
                                              activation_input=metadata,
                                              original_method =
                                                d.metadata.right[k])

        return d

