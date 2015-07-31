import argparse

import mir3.data.linear_decomposition as ld
import mir3.data.metadata as md
import mir3.lib.median_filtering as mf
import mir3.module

class Median(mir3.module.Module):
    """Applies median filtering on a linear decomposition.
    """

    def get_help(self):
        return """applies median filtering on a linear decomposition"""

    def build_arguments(self, parser):
        parser.add_argument('window', type=float, help="""length of median
                             window""")
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""input linear decomposition file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""output linear decomposition file""")

    def run(self, args):
        d = self.median_filter(ld.LinearDecomposition().load(args.infile),
                          args.window,
                          False)
        meta = md.FileMetadata(args.infile)
        for k, data, metadata in d.right():
            metadata.activation_input = meta
        d.save(args.outfile)

    def median_filter(self, d, window, save_metadata=True):
        """Alters the given linear decomposition, applying a median filter.

        The filtering process is done in the time domain.

        The argument provided is destroyed.

        Args:
            d: LinearDecomposition object to filter.
            window: window length.
            save_metadata: flag indicating whether the metadata should be
                           computed. Default: True.

        Returns:
            Same decomposition given in arguments.
        """
        if save_metadata:
            metadata = md.ObjectMetadata(a)
        else:
            metadata = None

        meta = md.Metadata(name="median_filter_length",
                           window=window,
                           activation_input=metadata,
                           original_method=None)

        # Binarizes the data and adjusts the metadata
        for k in d.data.right.keys():
            d.data.right[k] = \
                mf.median_filter_centered(d.data.right[k].transpose(),\
                window).transpose()
            d.metadata.right[k] = md.Metadata(method="median_filter_length",
                                              window=window,
                                              activation_input=metadata,
                                              original_method =
                                                d.metadata.right[k])

        return d

