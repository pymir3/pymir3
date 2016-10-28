from model_testing import ModelTester, ModelTesterInput
from sklearn.svm import SVC
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


class SimpleModelTester(ModelTester):

    def __init__(self):
        pass

    def test(self, test_data):
        model_filename = self.params['general']['scratch_directory'] + "/" + self.params['model_training']['output_model']

        model_file = open(model_filename)
        model = dill.load(model_file)
        model_file.close()

        scaler_file = open( ('%s.scaler' % model_filename))
        scaler = dill.load(scaler_file)
        scaler_file.close()

        features = scaler.transform(test_data.features)

        predicted = model.predict(features)

        print("Confusion matrix:")
        
        cm = confusion_matrix(input.truth, input.predicted)

        print_cm(cm, model.classes_)

        #output predict file
        predict_filename = self.params['general']['predict_file']
        print "outputting predicted classes to file %s" % (predict_filename)
        predict_file = open(predict_filename, "w")
        for i in xrange(len(predicted)):
            predict_file.write("%s\t%s\n" % (test_data.filenames[i], predicted[i]))

        predict_file.close()

        if hasattr(model, "predict_proba"):

            if self.params['model_testing']['predict_proba_file'] != "":
                predicted_proba_filename = self.params['general']['scratch_directory'] + "/" +\
                                           self.params['model_testing']['predict_proba_file']
            else:
                predicted_proba_filename = predict_filename + ".proba"

            print "outputting predicted probability to file %s" % (predicted_proba_filename)
            prob = model.predict_proba(test_data.features)
            predicted_from_prob = numpy.argmax(prob, axis=1) + 1

            predict_proba_file = open(predicted_proba_filename, "w" )

            for i in xrange(len(prob)):
                predict_proba_file.write("%d " % (predicted_from_prob[i]))
                for k in prob[i]:
                    predict_proba_file.write("%f " % (k))
                predict_proba_file.write("\n")

            predict_proba_file.close()
        else:
            print "prediction probability output not supported by the model."





