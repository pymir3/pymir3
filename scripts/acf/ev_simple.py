from evaluation import Evaluator, EvaluatorInput
from sklearn.metrics import confusion_matrix, classification_report
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
        print classification_report(input.truth, input.predicted)