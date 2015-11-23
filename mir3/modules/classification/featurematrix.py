import argparse
import csv
import numpy
import numpy.random

import mir3.data.feature_matrix as feature_matrix
import mir3.data.feature_track as track
import mir3.module

from sklearn.cross_validation import train_test_split, StratifiedKFold
from sklearn import mixture
from sklearn import svm
from sklearn import preprocessing

class FromFeatureMatrix(mir3.module.Module):
    def get_help(self):
        return """Classification experiments with a Feature Matrix using
                    GMMs (future work: implement others)"""

    def build_arguments(self, parser):
        parser.add_argument('database', type=argparse.FileType('rb'),
                            help="""input database""")
        parser.add_argument('labels', type=str,
                            help="""csv file with ground-truth labels""")
        parser.add_argument('-folds', '-f', type=int, default=2,
                            help="""number of folds for cross-validation""")

    def label_list(self, labelfile):
        file_label_dict = dict()
        lines = csv.reader(labelfile)
        for row in lines:
            file_label_dict[row[0]] = row[1]

        return file_label_dict

    def sort_labels(self, metadata, file_label_dict):
        labels = []
        for i in xrange(len(metadata.filename)):
            fname = metadata.filename[i].split('/')[-1]
            labels.append(int(file_label_dict[fname]))
        return labels

    def run(self, args):
        a = feature_matrix.FeatureMatrix().load(args.database)
        file_label_dict = self.label_list(open(args.labels, 'rb'))

        labels = self.sort_labels(a.metadata, file_label_dict)
        norm_data = preprocessing.normalize(preprocessing.scale(a.data))

        #data_train, data_test, label_train, label_test =\
        #    train_test_split(preprocessing.normalize\
        #         (preprocessing.scale(a.data)), labels, train_size=.5)

        skf = StratifiedKFold(labels, n_folds=2)
        for train_index, test_index in skf:
            data_train, data_test = norm_data[train_index,:],\
                        norm_data[test_index,:]

            label_train, label_test = [labels[x] for x in train_index],\
                                        [labels[x] for x in test_index]



        C = self.classify_svm(data_train, label_train, data_test, label_test)
        print "Accuracy:", 100*C, "%"


    def classify_gmm(self, train_in, train_cl, test_in, test_cl):
        """Run a GMM-based classification experiment.

        Returns:
        * precision (fraction of correct classifications)
        """
        # Training
        labels = set(train_cl)
        n_labels = len(labels)
        mixtures = []
        mixture_labels = []
        for k in labels:
            data = [train_in[i] for i in xrange(len(train_cl))\
                        if train_cl[i] == k]

            g = mixture.GMM(covariance_type='diag',
                        n_components = max(1, min(5, len(data)-2)),
                        min_covar = 0.01)
            g.fit(data)
            mixtures.append(g)
            mixture_labels.append(k)

        # Testing
        output_labels = []
        for d in xrange(len(test_cl)):
            prob = []
            for m in xrange(len(mixtures)):
                prob.append(mixtures[m].score(test_in[d,:])[0])
            output_labels.append(prob.index(max(prob))+1)

        # Evaluation
        hits = 0
        for x in xrange(len(output_labels)):
            if output_labels[x] == test_cl[x]:
                hits += 1

        # Precision
        return hits / float(len(output_labels))

    def classify_svm(self, train_in, train_cl, test_in, test_cl):
        """Run an SVM-based classification experiment.

        Returns:
        * precision (fraction of correct classifications)
        """
        # Training
        s = svm.SVC(C=100., tol=10**(-4.), decision_function_shape='ovr')#, class_weight='balanced')
        s = s.fit(train_in, train_cl)

        # Evaluation
        hits = 0
        output_labels = s.predict(test_in)
        for x in xrange(len(output_labels)):
            if output_labels[x] == test_cl[x]:
                hits += 1

        # Precision
        return hits / float(len(output_labels))
















