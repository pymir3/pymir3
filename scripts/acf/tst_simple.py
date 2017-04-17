from model_testing import ModelTester, ModelTesterInput
from sklearn.svm import SVC
import time
import numpy
import dill
from dft_net import sigtia_net

class SimpleModelTester(ModelTester):

    def __init__(self):
        pass

    def test(self, test_data):
        model_filename = self.params['general']['scratch_directory'] + "/" + self.params['model_training']['output_model']
        label_dict = self.params['general']['scratch_directory'] + "/" + self.params['model_testing']['label_dict']

        model_file = open(model_filename)
        model = dill.load(model_file)
        model_file.close()

        scaler_file = open( ('%s.scaler' % model_filename))
        scaler = dill.load(scaler_file)
        scaler_file.close()


        if test_data.type == 'matrix':

            if self.params['model_training']['model_trainer'] == "sigtia_net":
                params = model
                ld_file = open(label_dict)
                l_dict = dill.load(ld_file)
                ld_file.close()
                hidden_neurons = self.params['sigtia_net']['hidden_neurons']
                hidden_layers = self.params['sigtia_net']['hidden_layers']
                dropout_rate = self.params['sigtia_net']['dropout_rate']
                model = sigtia_net.SigtiaNET((None, test_data.features.shape[1]), len(l_dict.keys()),
                     hidden_neurons=hidden_neurons, hidden_layers=hidden_layers, dropout_rate=dropout_rate)
                model.set_params(params)
                
            features = scaler.transform(test_data.features)

            predicted = model.predict((features.astype('float32'), None))
            print predicted.shape
            if self.params['model_training']['model_trainer'] == "sigtia_net":
                predicted = predicted.argmax(axis=1)


            #TODO: na verdade esse esquema de voltar as labels deve ser feito de forma independente se o tipo eh matrix ou tracks
            #na HMM eu fiz diferente (ver abaixo....)
            #acho que o esquema do arquivo eh melhor...
            if label_dict is not None:
                l_dict = dill.load(open(label_dict))
                inv_ldict = dict()
                for i, l in enumerate(l_dict.keys()):
                    inv_ldict[i] = l
                predicted = [inv_ldict[i] for i in predicted]

        else:

            if test_data.type == 'tracks':

                all_tests = numpy.array(test_data.features[0])
                train_lengths = [test_data.features[0].shape[0]]
                for i in xrange(1, len(test_data.features)):
                    all_tests = numpy.vstack( (all_tests, numpy.array(test_data.features[i])) )
                    train_lengths.append(test_data.features[i].shape[0])

                X_test = [ scaler.transform(test_data.features[i]) for i in xrange(len(test_data.features)) ]

                predicted = [ model.predict(X_test[i]) for i in xrange(len(X_test)) ]

	if hasattr(model, "n_dic"):
	    if model.n_dic != None:
	        predicted = model.numbers_to_labels(predicted)

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





