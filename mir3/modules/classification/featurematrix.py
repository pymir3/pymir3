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
try:
    from sklearn import neural_network
except:
    pass

from sklearn import preprocessing
from sklearn import pipeline

class FromFeatureMatrix(mir3.module.Module):
    def get_help(self):
        return """Classification experiments with a Feature Matrix using
                    GMMs (future work: implement others)"""

    def build_arguments(self, parser):
        parser.add_argument('algorithm', choices=['gmm', 'rbm', 'svm'],
                            help="""Classification method to use""")
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
        ldict = {}

        for i in xrange(len(metadata.filename)):
            fname = metadata.filename[i].split('/')[-1]
            if file_label_dict[fname] in ldict:
                ldict[file_label_dict[fname]] += 1
            else:
                ldict[file_label_dict[fname]] = 1

        k = ldict.keys()

        for i in xrange(len(metadata.filename)):
            fname = metadata.filename[i].split('/')[-1]
            if ldict[file_label_dict[fname]] > 3:
                labels.append(k.index(file_label_dict[fname]))

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

        if args.algorithm == 'svm':
            classifier = self.classify_svm
        elif args.algorithm == 'rbm':
            classifier = self.classify_rbm
        elif args.algorithm == 'gmm':
            classifier = self.classify_gmm

        C1 = classifier(data_train, label_train, data_test, label_test)
        C2 = classifier(data_test, label_test, data_train, label_train)
        print "Accuracy:", 50*(C1+C2), "%"

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
                        n_components = max(1, min(10, len(data)-2)),
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


    def classify_rbm(self, train_in, train_cl, test_in, test_cl):
        """Run a Restricted Boltzmann Machine-based classification experiment.

        Returns:
        * precision (fraction of correct classifications)
        """
        # Training
        i = min((numpy.min(train_in), numpy.min(test_in)))
        train_in -= i
        test_in -= i

        m = max((numpy.max(train_in), numpy.max(test_in)))
        train_in /= float(m)
        test_in /= float(m)

        labels = set(train_cl)
        n_labels = len(labels)
        mixtures = []
        mixture_labels = []
        r = neural_network.BernoulliRBM(n_components=2000,
               learning_rate=10**(-3.), batch_size=10, n_iter=50)

        s = svm.SVC(C=100., tol=10**(-4.), kernel='poly', degree=1,
                coef0=1.0, gamma=1.0, decision_function_shape='ovr')

        classifier = pipeline.Pipeline(steps=[('rbm', r), ('svc', s)])
        classifier.fit(train_in, train_cl)

        # Evaluation
        hits = 0
        output_labels = classifier.predict(test_in)
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
        s = svm.SVC(C=100., tol=10**(-4.), kernel='poly', degree=1,
                coef0=1.0, gamma=1.0, decision_function_shape='ovr')
        #s = svm.LinearSVC(C=100., tol=10**(-4.))
        s = s.fit(train_in, train_cl)

        # Evaluation
        hits = 0
        output_labels = s.predict(test_in)
        for x in xrange(len(output_labels)):
            if output_labels[x] == test_cl[x]:
                hits += 1

        # Precision
        return hits / float(len(output_labels))
















