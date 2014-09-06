import argparse

import mir3.data.linear_decomposition as ld
import mir3.module

class Extract(mir3.module.Module):
    def get_help(self):
        return """extracts the left or right side of a linear decomposition"""

    def build_arguments(self, parser):
        parser.add_argument('side', choices=['left', 'right'], help="""side of
                            the linear decomposition to be kept""")
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""input file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""output file with one side cleared""")

    def run(self, args):
        d = ld.LinearDecomposition().load(args.infile)
        new_d = self.extract(d, args.side)
        new_d.save(args.outfile)

    def extract(self, d, side):
        """Extracts one side of a linear decomposition.

        The variables are only assigned, not copied. Any change to one object
        affects both the input and output.

        Args:
            d: LinearDecomposition object.
            side: name of the side that must be kept. Must be 'left' or 'right'.

        Returns:
            new LinearDecomposition object with the other side clear.

        Raises:
            ValueError: argument 'side' isn't either 'left' or 'right'.
        """
        new_d = ld.LinearDecomposition()

        if side == 'left':
            new_d.data.left = d.data.left
            new_d.metadata.left = d.metadata.left
        elif side == 'right':
            new_d.data.right = d.data.right
            new_d.metadata.right = d.metadata.right
        else:
            raise ValueError("Invalid side '%r'." % side)

        return new_d
