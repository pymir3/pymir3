import mir3.data.blank as blank
import mir3.data.data_object as do
import mir3.data.metadata as md

class Evaluation(do.DataObject):
    """Evaluation result between 2 scores.

    Provides default performance measurements of an estimation algorithm given a
    reference.

    Metadata available:
        -estimated: estimated score's metadata. Default: None.
        -estimated_input: estimated score input metadata. Default: None.
        -method: information about the method used for comparing the scores.
                 Default: None.
        -reference: reference score's metadata. Default: None.
        -reference_input: reference score input metadata. Default: None.

    Data available:
        -n_correct: number of correct estimates.
        -n_estimated: number of estimated notes.
        -n_reference: number of reference notes.
        -precision: estimate's precision.
        -recall: estimate's recall.
        -f: estimate's f-score.
    """

    def __init__(self, n_estimated=0, n_reference=0, n_correct=0):
        """Sets the evaluation data.

        Args:
            n_estimated: number of estimated notes. Default: 0.
            n_reference: number of reference notes. Default: 0.
            n_correct: number of correctly estimated notes. Default: 0.
        """
        super(Evaluation, self).__init__(
                md.Metadata(estimated=None,
                            estimated_input=None,
                            method=None,
                            reference=None,
                            reference_input=None))

        recall = float(n_correct)/n_reference if n_reference > 0 else 0
        precision = float(n_correct)/n_estimated if n_estimated > 0 else 0
        f = 2*recall*precision/(recall+precision) if recall+precision > 0 else 0

        self.data = blank.Blank(n_correct=n_correct,
                                n_estimated=n_estimated,
                                n_reference=n_reference,
                                precision=precision,
                                recall=recall,
                                f=f)
