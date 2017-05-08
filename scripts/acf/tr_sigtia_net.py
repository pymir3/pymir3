from sklearn.grid_search import GridSearchCV
from model_training import ModelTrainer, ModelTrainerInput
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectPercentile
from sklearn.feature_selection import f_classif as anova
from sklearn.cross_validation import ShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.cross_validation import train_test_split

from dft_net import sigtia_net
import time
import dill
import numpy as np

class SigtiaNetModelTrainer(ModelTrainer):

    def __init__(self):
        pass


    def train(self, train_data):
        """
        :param train_data:
        :type train_data: ModelTrainerInput
        """

        label_dict_file = self.params['general']['scratch_directory'] + "/" + self.params['model_testing']['label_dict']
        out_filename = self.params['general']['scratch_directory'] + "/" + self.params['model_training']['output_model']
        hidden_neurons = self.params['sigtia_net']['hidden_neurons']
        hidden_layers = self.params['sigtia_net']['hidden_layers']
        dropout_rate = self.params['sigtia_net']['dropout_rate']
        early_stopping = self.params['sigtia_net']['early_stopping']
        max_epochs = self.params['sigtia_net']['max_epochs']
        batch_size = self.params['sigtia_net']['batch_size']

        print "training model with SigtiaNET..."

        T0 = time.time()
        features = train_data.features.astype('float32')
        labels = train_data.labels
	distinct_labels = sorted(set(labels))
	distinct_labels_n = len(distinct_labels)

        scaler = StandardScaler()
        scaler.fit(features)
        features = scaler.transform(features)

	estimator = sigtia_net.SigtiaNET((None, features.shape[1]), distinct_labels_n, hidden_neurons=hidden_neurons, hidden_layers=hidden_layers,dropout_rate=dropout_rate)

        #converter labels para o formato matricial 
        #(linhas sao os exemplos, colunas indicam as classes - 1 indica que aquele exemplo e daquela classe :)
        label_dict = dict()
	for i, l in enumerate(distinct_labels):
            label_dict[l] = i
        #print label_dict, distinct_labels, distinct_labels_n

        dill.dump(label_dict, open(label_dict_file, 'w'))

	labels = [label_dict[l] for l in labels]
	Y_M = np.zeros((len(labels), distinct_labels_n))
	k = np.arange(len(labels))
	Y_M[k, labels] = 1
	labels = Y_M.astype('float32')

        X_train, X_val, Y_train, Y_val = train_test_split(features, labels, test_size=0.2)

        estimator.fit((X_train, Y_train), (X_val, Y_val), max_epochs=max_epochs, early_stopping=early_stopping, batch_size=batch_size)
        T1 = time.time()

        print "model training took %f seconds" % (T1-T0)
        print "saved model parameters to %s" % (out_filename)
        outfile = open(out_filename, "w")
        dill.dump(estimator.get_params(), outfile, dill.HIGHEST_PROTOCOL )

        outfile_scaler = open('%s.scaler' % out_filename, "w")
        dill.dump(scaler, outfile_scaler, dill.HIGHEST_PROTOCOL)


        print label_dict, distinct_labels_n


