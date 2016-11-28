from evaluation import Evaluator, EvaluatorInput
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import time
import numpy
import dill

from sklearn.metrics import confusion_matrix

def print_cm(cm, labels, hide_labels=True, file=None, hide_zeroes=False, hide_diagonal=False, hide_threshold=None):
    """pretty print for confusion matrixes"""
    #TODO: implementar hide_labels para saida em arquivo
    columnwidth = max([len(x) for x in labels]+[0]) # 5 is value length

    if hide_labels:
        columnwidth = 3

    empty_cell = " " * columnwidth
    # Print header
    if file is None:
        print "    " + empty_cell,
    else:
        file.write("    " + empty_cell)
    i = 0
    for label in labels:
        if file is None:
            if hide_labels:
                print "%{0}d".format(columnwidth) % i,
            else:
                print "%{0}s".format(columnwidth) % label,
        else:
            file.write("%{0}s".format(columnwidth) % label)
        i+=1
    if file is None:
        print
    else:
        file.write("\n")
    # Print rows
    for i, label1 in enumerate(labels):
        if file is None:
            if hide_labels:
                print "    %{0}d".format(columnwidth) % i,
            else:
                print "    %{0}s".format(columnwidth) % label1,
        else:
            file.write("    %{0}s".format(columnwidth) % label1)
        for j in range(len(labels)):
            cell = "%{0}d".format(columnwidth) % cm[i, j]
            if hide_zeroes:
                cell = cell if float(cm[i, j]) != 0 else empty_cell
            if hide_diagonal:
                cell = cell if i != j else empty_cell
            if hide_threshold:
                cell = cell if cm[i, j] > hide_threshold else empty_cell
            if file is None:
                print cell,
            else:
                file.write(cell)
        if file is None:
            print
        else:
            file.write("\n")

    for i, l in enumerate(labels):
        print "%d: %s" % (i, l)

class SimpleEvaluator(Evaluator):

    def __init__(self):
        pass

    def evaluate(self, input):
        """
        :param input:
        :type input: EvaluatorInput
        """

        print("Confusion matrix:")

        cm = confusion_matrix(input.truth, input.predicted)

        print_cm(cm, sorted(list(set(input.truth))))

        print accuracy_score(input.truth, input.predicted)
        print classification_report(input.truth, input.predicted)