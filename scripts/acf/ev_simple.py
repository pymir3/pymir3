from evaluation import Evaluator, EvaluatorInput
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import time
import numpy
import dill

class SimpleEvaluator(Evaluator):

    def __init__(self):
        pass

    def evaluate(self, input):
        """
        :param input:
        :type input: EvaluatorInput
        """
        print accuracy_score(input.truth, input.predicted)
        print classification_report(input.truth, input.predicted)