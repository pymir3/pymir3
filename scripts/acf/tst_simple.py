from model_testing import ModelTester, ModelTesterInput
from sklearn.svm import SVC
import time
import numpy
import dill

from sklearn.metrics import confusion_matrix

class SimpleModelTester(ModelTester):

    def __init__(self):
        pass

    def test(self, test_data):
        model_filename = self.params['general']['scratch_directory'] + "/" + self.params['model_training']['output_model']

        model_file = open(model_filename)
        model = dill.load(model_file)
        model_file.close()

        predicted = model.predict(test_data.features)

        #output predict file
        predict_filename = self.params['general']['scratch_directory'] + "/" + self.params['model_testing']['predict_file']
        print "outputting predicted classes to file %s" % (predict_filename)
        predict_file = open(predict_filename, "w")
        for i in xrange(len(predicted)):
            predict_file.write("%s\t%s\n" % (test_data.filenames[i], predicted[i]))

        predict_file.close()

        if hasattr(model, "predict_proba"):
            predicted_proba_filename = self.params['general']['scratch_directory'] + "/" + self.params['model_testing'][
                'predict_proba_filelist'];
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





