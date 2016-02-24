import mir3.data.evaluation as evaluation
import mir3.module

class EvaluationCSV(mir3.module.Module):
    """CSV evaluation printing.
    """

    def get_help(self):
        return """print information about several evaluation files as a CSV"""

    def build_arguments(self, parser):
        parser.add_argument('-H','--no_header', action='store_true',
                            default=False, help="""don't print the header
                            line""")
        parser.add_argument('-s','--short_filenames', action='store_true',
                            default=False, help="""don't print directory names
                            and extensions from filenames""")

        parser.add_argument('infile', nargs='+', help="""evaluation files""")

    def run(self, args):
        e = evaluation.Evaluation()

        if not args.no_header:
            print "Info,N_estimated,N_reference,N_Correct,Recall,Precision,"\
                  "F-Measure"

        for name in sorted(args.infile):
            with open(name, 'rb') as f:
                e = e.load(f)
            name = e.metadata.reference_input.name
            if args.short_filenames:
                name = name.split('/')
                name = name[-1]
                name = name.split('.')
                name = name[0]

            print "%s,%d,%d,%d,%.13f,%.13f,%.13f" % (name, e.data.n_estimated,
                                                     e.data.n_reference,
                                                     e.data.n_correct,
                                                     e.data.recall,
                                                     e.data.precision, e.data.f)
