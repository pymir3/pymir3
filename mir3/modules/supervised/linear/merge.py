import argparse

import mir3.data.linear_decomposition as ld
import mir3.module

class Merge(mir3.module.Module):
    def get_help(self):
        return """merge linear decomposition files"""

    def build_arguments(self, parser):
        parser.add_argument('infile', nargs='+', help="""linear decomposition
                            file to be merged""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""merged linear decomposition file""")

    def run(self, args):
        d_list = []
        for filename in args.infile:
            with open(filename, 'rb') as handler:
                d_list.append(ld.LinearDecomposition().load(handler))

        new_d = self.merge(d_list)

        new_d.save(args.outfile)

    def merge(self, decompositions_list):
        """Merges the linear decompositions given into a single one.

        Args:
            decompositions_list: a list of linear decompositions to be merged.

        Returns:
            LinearDecomposition object with inputs merged.
        """
        d = ld.LinearDecomposition()

        for other in decompositions_list:
            for key, data, metadata in other.left():
                d.add(key, left=data, left_metadata=metadata)
            for key, data, metadata in other.right():
                d.add(key, right=data, right_metadata=metadata)

        return d
