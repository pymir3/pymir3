import numpy

import mir3.data.linear_decomposition as ld
import mir3.module

class Tests(mir3.module.Module):

    def get_help(self):
        return """computes the values at which the threshold should be tested"""

    def build_arguments(self, parser):
        parser.add_argument('-n','--number-values', default=10, type=int,
                            help="""number of thresholds to consider (default:
                            %(default)s)""")
        parser.add_argument('--use-max', action='store_true', default=False,
                            help="""use the maximum for the upper threshold
                            bound, otherwise use another statistic based on
                            outlier detection""")

        parser.add_argument('infile', nargs='+', help="""linear decomposition
                            files""")

    def run(self, args):
        decompositions = []
        for filename in args.infile:
            with open(filename, 'rb') as handler:
                decompositions.append(
                        ld.LinearDecomposition().load(handler))

        for level in self.get_levels(decompositions,
                                     args.number_values,
                                     args.use_max):
            print level

    def get_levels(self, decompositions, number_values, use_max=False):
        """Computes threshold levels that should be tested.

        Based on a list of linear decompositions, uses some heuristics to find
        good threshold values.

        Args:
            decompositions: list of decompositions used to compute thresholds.
            number_values: number of threshold values.
            use_max: flag indicating that the maximum value of the activations
                     should be the upper bound.

        Returns:
            Numpy nparray with the thresholds.
        """
        # Initialized bounds
        minLevel = float('-inf')
        maxLevel = float('-inf')

        # Evaluates each decomposition
        for d in decompositions:
            # Evaluates intruments one at a time
            instruments = set([k[0] for k in d.data.right.keys()])
            for instrument in instruments:
                A_instrument = [] # Activation for the instrument

                # Evaluates each note
                notes = set([k[1] for k in d.data.right.keys()
                                  if k[0] == instrument])
                for note in notes:
                    # For now, if the activation has more than one line, just
                    # merges them all
                    datas = [d.data.right[k].reshape(-1)
                             for k in d.data.right.keys()
                             if k[0] == instrument and k[1] == note]

                    A = numpy.hstack(datas) # Activations for the note
                    A_instrument.append(A)
                A_instrument = numpy.hstack(A_instrument)

                # Levels can only increase as we move from one instrument to
                # another.

                # Chooses method to compute max activation
                if use_max:
                    maxLevel = max(maxLevel, numpy.max(A_instrument))
                else:
                    maxLevel = max(maxLevel, numpy.mean(A_instrument) + \
                                             5*numpy.std(A_instrument))

                minLevel = max(minLevel, numpy.mean(A_instrument))

        # Gets a range of levels to test
        return numpy.linspace(minLevel, maxLevel, number_values)
