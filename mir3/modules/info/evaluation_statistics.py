import numpy

import mir3.data.evaluation as evaluation
import mir3.module

class EvaluationStatistics(mir3.module.Module):
    def get_help(self):
        return """gather statistics from the evaluation files"""

    def build_arguments(self, parser):
        parser.add_argument('infile', nargs='+', help="""evaluation files""")

    def run(self, args):
        e = evaluation.Evaluation()

        r = []
        p = []
        f = []

        for name in args.infile:
            with open(name, 'rb') as h:
                e = e.load(h)
            r.append(e.data.recall)
            p.append(e.data.precision)
            f.append(e.data.f)

        print "Recall:    mean=%f, std_dev=%f" % (numpy.mean(r), numpy.std(r))
        print "Precision: mean=%f, std_dev=%f" % (numpy.mean(p), numpy.std(p))
        print "F-Measure: mean=%f, std_dev=%f" % (numpy.mean(f), numpy.std(f))
