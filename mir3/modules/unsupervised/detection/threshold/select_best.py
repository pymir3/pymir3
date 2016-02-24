import mir3.data.evaluation as evaluation
import mir3.module

class SelectBest(mir3.module.Module):
    def get_help(self):
        return """retrieves the best threshold according to an exhaustive
               evaluation"""

    def build_arguments(self, parser):
        parser.add_argument('infile', nargs='+', help="""evaluation files""")

    def run(self, args):
        for filename in args.infile:
            with open(filename, 'rb') as handler:
                self.add(evaluation.Evaluation().load(handler))

        best_th, mean_f = self.get_best()
        print best_th

    def __init__(self):
        self.f_thresholds = {}
        self.n_thresholds = {}

    def add(self, evaluation):
        """Adds a set of evaluations to be compared.

        The threshold for each evaluation is used as an identifier so that we
        can merge the results of many evaluations.

            evaluation: single evaluation object or a list of evaluations.

        Returns:
            self
        """
        if isinstance(evaluation,list):
            for e in evaluation:
                self.add(e)
            return

        th = evaluation.metadata.method.id
        if th in self.f_thresholds.keys():
            self.f_thresholds[th] += evaluation.data.f
            self.n_thresholds[th] += 1.0
        else:
            self.f_thresholds[th] = evaluation.data.f
            self.n_thresholds[th] = 1.0

        return self

    def get_best(self):
        """Computes the best threshold based on the mean f value.

        Takes the mean f values of all evaluations sharing thresholds. Note that
        there may be different numbers of evaluations for each threshold.

        Args:
            evaluations: list of evaluations used to choose tht threshold.

        Returns:
            Tuple of (best threshold, best mean f value)
        """
        best_f = 0.0
        best_th = 0.0
        #print "Evaluating thresholds..."
        #print "Thresholds to evaluate:", self.f_thresholds
        for th in self.f_thresholds:
            #print th, self.f_thresholds[th]/self.n_thresholds[th]
            if self.f_thresholds[th] > best_f:
                best_f = self.f_thresholds[th]
                best_th = th

        return best_th, self.f_thresholds[best_th]/self.n_thresholds[best_th]
