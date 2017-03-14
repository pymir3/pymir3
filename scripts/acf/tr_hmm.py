from model_training import ModelTrainer, ModelTrainerInput

from sklearn.preprocessing import StandardScaler
import time
import dill
import numpy as np
import copy
import hmmlearn
from hmmlearn.hmm import GaussianHMM, MultinomialHMM
from sklearn import preprocessing

import warnings
warnings.filterwarnings('ignore')

from multiprocess import Pool

class MultipleHMM():
    base_model = None
    
    def __init__(self, base_model=None):
        self.base_model = base_model
        self.label_dic = None
        self.n_dic = None
        self.models = {}

    def label_to_numbers(self, labels):
        if self.label_dic == None:
            self.label_dic = dict()
            self.n_dic = dict()
            i = 0
            for l in labels:
                if l not in self.label_dic:
                    self.label_dic[l] = i
                    self.n_dic[i] = l
                    i+=1

        return [self.label_dic[i] for i in labels]

    def numbers_to_labels(self, numbers):
        return [self.n_dic[i] for i in numbers]    

    def __thread_fit(self, work):
        m = work[0]
        x = work[1]
        l = work[2]

        return m.fit(x,l)

    def fit(self, X, y, train_lengths, workers=4):
        """Fits all internal models"""
        labels = set(y)
        work = []

        for l in labels:
            print "Training label:", l
            l_index = [i for i in xrange(len(y)) if y[i] == l]
            if X[0].ndim == 1:
                this_x = [X[i].reshape(-1, 1) for i in l_index]
            else:
                this_x = [X[i] for i in l_index]
                
            this_lengths = [train_lengths[i] for i in l_index]
            
            my_x = this_x[0]
            for i in xrange(1, len(this_x)):
                my_x = np.vstack ((my_x, np.array(this_x[i])))
            
            new_model = copy.deepcopy(self.base_model)

            work.append( (new_model, my_x, this_lengths) )

        if workers > 0:
            pool = Pool(workers)
            models = pool.map(self.__thread_fit, work)
            for i in xrange(len(models)):
                self.models[i] = models[i]
        else:

            for i in xrange(len(work)):
                self.models[i] = self.__thread_fit(work[i])
        
    
    def predict(self, X):
        """Predicts a label for input X"""
        return_label = None
        best_prob = None
        #print "There are %d HMM models." % len(self.models.keys())
        for label in self.models.keys():
            
            #print "Computing probabilities on shape", X.shape
            if X.ndim == 1:
                this_prob = self.models[label].score(X.reshape(-1,1))
            else:
                this_prob = self.models[label].score(X)
            
            #print "Prob in label", label, "=", this_prob
            if (best_prob is None) or (this_prob > best_prob):
                best_prob = this_prob
                return_label = label
        return return_label

class HmmModelTrainer(ModelTrainer):

    def __init__(self):
        pass

    def train(self, train_data):
        """
        :param train_data:
        :type train_data: ModelTrainerInput
        """

        n_components = self.params['hmm']['n_components']
        ct = self.params['hmm']['covariance_type']
        n_iter = self.params['hmm']['n_iter']

        cl = MultipleHMM(GaussianHMM(n_components=n_components, covariance_type=ct, n_iter=n_iter))

        features = train_data.features
        labels = train_data.labels

        if not isinstance( labels, ( int, long ) ):
            labels = cl.label_to_numbers(labels)

        if train_data.type != 'tracks':
            print('ERROR: input to HMM training procedure must be a list of feature tracks.')
            exit(1)

        all_trains = np.array(features[0])
        train_lengths = [features[0].shape[0]]
        for i in xrange(1, len(features)):
            all_trains = np.vstack( (all_trains, np.array(features[i])) )
            train_lengths.append(features[i].shape[0])

        scaler = StandardScaler().fit(all_trains)

        X_train = [scaler.transform(features[i]) for i in xrange(len(features))]

        cl.fit(X_train, labels, train_lengths, workers=self.params['hmm']['n_workers'])

        out_filename = self.params['general']['scratch_directory'] + "/" + self.params['model_training']['output_model']
        outfile = open(out_filename, "w")
        dill.dump(cl, outfile, dill.HIGHEST_PROTOCOL )
        outfile.close()

        outfile_scaler = open('%s.scaler' % out_filename, "w")
        dill.dump(scaler, outfile_scaler, dill.HIGHEST_PROTOCOL)
        outfile_scaler.close()
