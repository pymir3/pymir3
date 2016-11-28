from sklearn.grid_search import GridSearchCV
from model_training import ModelTrainer, ModelTrainerInput
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectPercentile
from sklearn.feature_selection import f_classif as anova
from sklearn.cross_validation import ShuffleSplit
from sklearn.preprocessing import StandardScaler
import time
import dill
import numpy as np

class SvmRegModelTrainer(ModelTrainer):

    def __init__(self):
        pass


    def train(self, train_data):
        """
        :param train_data:
        :type train_data: ModelTrainerInput
        """

        probability = self.params['svm_reg']['probability']

        if self.params['svm_reg']['balanced_class_weights']:
            svmc = SVC(kernel='rbf', probability=probability, class_weight='balanced')
        else:
            svmc = SVC(kernel='rbf', probability=probability)

        Cs = self.params['svm_reg']['Cs']
        gammas = self.params['svm_reg']['gammas']
        out_filename = self.params['general']['scratch_directory'] + "/" + self.params['model_training']['output_model']

        print "training model with SVM and grid search (%d combinations)..." % (len(Cs) * len(gammas))
        print "using ANOVA feature selection"
        print "training set size: %d, # of features: %d" % (len(train_data.labels), train_data.features.shape[1])
        print "gammas: ", gammas
        print "C:", Cs

        T0 = time.time()
        features = train_data.features
        labels = train_data.labels

        transform = SelectPercentile(anova)
        scaler = StandardScaler()
        clf = Pipeline([ ('standardizer', scaler ), ('anova', transform), ('svm', svmc)])

        percentiles = (np.arange(11) * 10)[1:]

        cv = ShuffleSplit(len(train_data.labels), n_iter=10, test_size=0.2, random_state=0)
        estimator = GridSearchCV(clf,
                                 dict(anova__percentile=percentiles,
                                      svm__gamma=gammas,
                                      svm__C=Cs),
                                 cv=cv,
                                 n_jobs=self.params['svm_reg']['num_workers'])
        scaler.fit(features)
        features = scaler.transform(features)
        estimator.fit(features, labels)
        T1 = time.time()

        print "model training took %f seconds" % (T1-T0)
        print "best model score: %f" % (estimator.best_score_)
        best_percentile = estimator.best_estimator_.named_steps['anova'].percentile
        best_c = estimator.best_estimator_.named_steps['svm'].C
        best_gamma = estimator.best_estimator_.named_steps['svm'].gamma
        print "best params found for SVM: C = %.2ef, gamma = %.2ef" % (best_c, best_gamma)
        print "best params found for ANOVA: percetile = %d" % (best_percentile)
        print "saved best model to %s" % (out_filename)
        outfile = open(out_filename, "w")
        dill.dump(estimator.best_estimator_, outfile, dill.HIGHEST_PROTOCOL )

        outfile_scaler = open('%s.scaler' % out_filename, "w")
        dill.dump(scaler, outfile_scaler, dill.HIGHEST_PROTOCOL)

        #dill.dump( StandardScaler().fit(features) )



