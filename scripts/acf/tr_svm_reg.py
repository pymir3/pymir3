from sklearn.grid_search import GridSearchCV
from model_training import ModelTrainer, ModelTrainerInput
from sklearn.svm import SVC
import time
import dill

class SvmRegModelTrainer(ModelTrainer):

    def __init__(self):
        pass


    def train(self, train_data):
        """
        :param train_data:
        :type train_data: ModelTrainerInput
        """

        probability = self.params['svm_reg']['probability']
        svmc = SVC(kernel='rbf', probability=probability)
        Cs = self.params['svm_reg']['Cs']
        gammas = self.params['svm_reg']['gammas']
        out_filename = self.params['general']['scratch_directory'] + "/" + self.params['model_training']['output_model']

        print "training model with SVM and grid search (%d combinations)..." % (len(Cs) * len(gammas))
        print "training set size: %d, # of features: %d" % (len(train_data.labels), train_data.features.shape[1])
        print "gammas: ", gammas
        print "C:", Cs

        T0 = time.time()
        features = train_data.features
        labels = train_data.labels

        estimator = GridSearchCV(svmc,
                                 dict(C=Cs,
                                      gamma=gammas),
                                 n_jobs=self.params['svm_reg']['num_workers'])
        estimator.fit(features, labels)
        T1 = time.time()

        print "model training took %f seconds" % (T1-T0)
        print "best model score: %f" % (estimator.best_score_)
        print "best params found: C = %.2ef, gamma = %.2ef" % (estimator.best_estimator_.C,estimator.best_estimator_.gamma)
        print "saved best model to %s" % (out_filename)
        outfile = open(out_filename, "w")
        dill.dump(estimator.best_estimator_, outfile, dill.HIGHEST_PROTOCOL )

