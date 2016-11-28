# -*- coding: utf-8 -*-

from sklearn.grid_search import GridSearchCV
from model_training import ModelTrainer, ModelTrainerInput
from sklearn.mixture import gmm
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectPercentile
from sklearn.feature_selection import f_classif as anova
import time
import dill
import numpy as np


class GMMClassifier():
    def __init__(self, n_classes):
        self.n_classes = n_classes
        self.mixtures = []

    def add_mixture(self, mixture, label):
        self.mixtures.append((label,mixture))

    def predict(self, X):
        # labels = []
        # for i in X:
        #     high = 0
        #     for k, (l, m) in enumerate(self.mixtures):
        #         if m.score(i) > m.score(high):
        #             high = k
        #     labels.append(self.mixtures[k][0])
        # return labels
        labels = []
        scores = None
        for m in self.mixtures:
            score = m[1].score(X)
            if scores is None:
                scores = np.array(score)
            else:
                scores = np.vstack((scores, score))
        predicted = np.argmax(scores, axis=0)
        for i in predicted:
            labels.append(self.mixtures[i][0])
        return labels



class GmmModelTrainer(ModelTrainer):

    def __init__(self):
        pass


    def train(self, train_data):
        """
        :param train_data:
        :type train_data: ModelTrainerInput
        """

        features = train_data.features
        labels = train_data.labels

        classes = sorted(set(labels))
        n_classes = len(set(labels))

        #arrumar: # de componentes é o número de features - 1 ?
        #n_components = self.params['gmm']['n_components'] if self.params['gmm']['n_components'] != -1 else max(1, min(10, len(set(features))-2))
        n_components = self.params['gmm']['n_components'] if self.params['gmm']['n_components'] != -1 else 20
        n_init = self.params['gmm']['n_init']
        out_filename = self.params['general']['scratch_directory'] + "/" + self.params['model_training']['output_model']
        min_covar = self.params['gmm']['min_covar']
        covariance_type = self.params['gmm']['covariance_type']

        #print "training model with GMM and grid search..."
        #print "using ANOVA feature selection"
        print "training set size: %d, # of features: %d" % (len(train_data.labels), train_data.features.shape[1])
        print "number of components: %d" % (n_components)

        #otimizar AIC / BIC para obter número ótimo de componentes

        np_labels = np.array(labels)


        T0 = time.time()

        cl = GMMClassifier(n_classes)

        print np_labels.shape, features.shape

        aic_nc = 0
        aic_menor = np.inf
        aic_val = 0

        for nc in [3, 5, 7, 10, 12, 15, 17,20,30]:
            print "training for nc = %d" % nc
            aic_val = 0
            for c in classes:
                #print c
                #print (np_labels == c)
                print "training mixture for class %s" % c
                c_features = features[np_labels == c]
                mix = gmm.GMM(n_components=nc,
                              min_covar=min_covar,
                              covariance_type=covariance_type,
                              n_init=n_init)
                mix.fit(c_features)
                #cl.add_mixture(mixture=mix.fit(c_features), label=c)
                #print mix.score_samples(features[np_labels == 'bus'])[0] > 0

                # otimizar AIC / BIC para obter número ótimo de componentes
                aic  = mix.aic(features[np_labels == c])
                #print aic
                aic_val += aic if aic > 0 else 0

            if aic_val < aic_menor:
                aic_menor = aic_val
                aic_nc = nc

            print "aic_val = %d for nc = %d" % (aic_val, nc)

        print "melhor aic = %d p/ nc = %d" % (aic_menor , aic_nc)

        for c in classes:
            print "training mixture for class %s" % c
            c_features = features[np_labels == c]
            mix = gmm.GMM(n_components=aic_nc,
                          min_covar=min_covar,
                          covariance_type=covariance_type,
                          n_init=n_init)

            cl.add_mixture(mixture=mix.fit(c_features), label=c)
            # print mix.score_samples(features[np_labels == 'bus'])[0] > 0

        T1 = time.time()

        print "model training took %f seconds" % (T1-T0)
        # print "best model score: %f" % (estimator.best_score_)
        # best_percentile = estimator.best_estimator_.named_steps['anova'].percentile
        # best_c = estimator.best_estimator_.named_steps['svm'].C
        # best_gamma = estimator.best_estimator_.named_steps['svm'].gamma
        # print "best params found for SVM: C = %.2ef, gamma = %.2ef" % (best_c, best_gamma)
        # print "best params found for ANOVA: percetile = %d" % (best_percentile)
        # print "saved best model to %s" % (out_filename)
        print "saved model to %s" % (out_filename)
        outfile = open(out_filename, "w")
        dill.dump(cl, outfile, dill.HIGHEST_PROTOCOL )

