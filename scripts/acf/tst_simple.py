from model_testing import ModelTester, ModelTesterInput
from sklearn.svm import SVC
import time
import numpy
import dill

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


        if test_data.type == 'matrix':

            features = scaler.transform(test_data.features)

            predicted = model.predict(features)

        else:

            if test_data.type == 'tracks':

                all_tests = numpy.array(test_data.features[0])
                train_lengths = [test_data.features[0].shape[0]]
                for i in xrange(1, len(test_data.features)):
                    all_tests = numpy.vstack( (all_tests, numpy.array(test_data.features[i])) )
                    train_lengths.append(test_data.features[i].shape[0])

                X_test = [ scaler.transform(test_data.features[i]) for i in xrange(len(test_data.features)) ]

                predicted = [ model.predict(X_test[i]) for i in xrange(len(X_test)) ]

        if model.n_dic != None:
            predicted = model.numbers_to_labels(predicted)

        print predicted


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





