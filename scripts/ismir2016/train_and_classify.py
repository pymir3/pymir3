#!/usr/bin/python
# -*- coding: utf8 -*-
import sys
sys.path.append("../../")
import mir3.data.feature_matrix as fm
import numpy as np
from sklearn import cross_validation
from sklearn import neighbors
from sklearn import svm
from sklearn import naive_bayes
from sklearn.feature_selection import SelectPercentile
from sklearn.feature_selection import f_regression
from sklearn.feature_selection import f_classif
from sklearn.decomposition import PCA
from sklearn.decomposition import RandomizedPCA
from sklearn.decomposition import KernelPCA
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix

def print_cm(cm, labels, file=None, hide_zeroes=False, hide_diagonal=False, hide_threshold=None):
    """pretty print for confusion matrixes"""
    columnwidth = max([len(x) for x in labels]+[5]) # 5 is value length
    empty_cell = " " * columnwidth
    # Print header
    if file is None:
        print "    " + empty_cell,
    else:
        file.write("    " + empty_cell)
    for label in labels:
        if file is None:
            print "%{0}s".format(columnwidth) % label,
        else:
            file.write("%{0}s".format(columnwidth) % label)
    if file is None:
        print
    else:
        file.write("\n")
    # Print rows
    for i, label1 in enumerate(labels):
        if file is None:
            print "    %{0}s".format(columnwidth) % label1,
        else:
            file.write("    %{0}s".format(columnwidth) % label1)
        for j in range(len(labels)):
            cell = "%{0}d".format(columnwidth) % cm[i, j]
            if hide_zeroes:
                cell = cell if float(cm[i, j]) != 0 else empty_cell
            if hide_diagonal:
                cell = cell if i != j else empty_cell
            if hide_threshold:
                cell = cell if cm[i, j] > hide_threshold else empty_cell
            if file is None:
                print cell,
            else:
                file.write(cell)
        if file is None:
            print
        else:
            file.write("\n")

def MIREX_TrainAndClassify():
    pass

class ClassificationSummary:

    def __init__(self, label_names):
        self.results = dict()
        self.label_names = label_names

    def add_result(self, pipeline_name, cr, accuracy, accuracy_stdev, labels, predicted, best_params, sorted_features):
        lines = cr.split("\n")
        data = filter(None,lines[-2].split(" "))
        self.results[pipeline_name] = dict()
        self.results[pipeline_name]['pipeline'] = pipeline_name
        self.results[pipeline_name]['accuracy'] = str(accuracy) + "+-" + str(accuracy_stdev)
        self.results[pipeline_name]['precision'] = data[3]
        self.results[pipeline_name]['recall'] = data[4]
        self.results[pipeline_name]['f1-score'] = data[5]
        self.results[pipeline_name]['labels'] = labels
        self.results[pipeline_name]['predicted'] = predicted
        self.results[pipeline_name]['best_params'] = str(best_params).replace(",", "//")
        self.results[pipeline_name]['sorted_features'] = str([x for x in sorted_features]).replace(",", "//")

    def to_csv(self, filename):
        outfile = open(filename, 'w')
        outfile.write("pipeline,best_params,accuracy,precision,recall,f1-score,sorted_features\n")
        for i in sorted(self.results.keys()):
            outfile.write(str(self.results[i]['pipeline']) + "," +
                          str(self.results[i]['best_params']) + "," +
                          str(self.results[i]['accuracy']) + "," +
                          str(self.results[i]['precision']) + "," +
                          str(self.results[i]['recall'])+ "," +
                          str(self.results[i]['f1-score']) + "," +
                          str(self.results[i]['sorted_features']) +
                          "\n")
        outfile.close()


def train_and_classify(csv_file=None, feature_matrix=None, sample_labels=None, cv_folds=10, n_processes=4):

    folds = cv_folds

    if csv_file is None and feature_matrix is None:
        sys.exit("Indique o csv ou a matriz de features do pymir3")

    if csv_file:
        csv = np.genfromtxt(csv_file, dtype='string' ,skip_header=1, delimiter=',')

        features = np.asfarray(csv.T[:-1].T)
        labels =  csv.T[-1:].T
        labels.shape = (labels.shape[0])

        print "number of features:", features.shape[1]

    if feature_matrix:

        features = feature_matrix.data

        features_names = np.array(feature_matrix.metadata.feature.split(" "))

        if sample_labels is None:
            sys.exit("É necessário informar o dicionário de labels quando a matriz de features é usada como entrada.")
        labels = []

        for i in feature_matrix.metadata.filename:
            labels.append(sample_labels[i])

        labels = np.array(labels)

    label_names = sorted([i for i in set(labels)])

    summary = ClassificationSummary(label_names)

    print "number of features:", features.shape[1]

    #classifiers
    knn = neighbors.KNeighborsClassifier(n_neighbors=1)
    svmc = svm.SVC(kernel='rbf', C=300)
    nb = naive_bayes.GaussianNB()

    print "\n@@@All Features"

    print "\n###NB"
    scores = cross_validation.cross_val_score(nb, features, labels, cv=folds)
    print("NB Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std()))
    predicted = cross_validation.cross_val_predict(nb, features, labels, cv=folds)
    cr = classification_report(labels, predicted)
    print cr
    summary.add_result("NB", cr, scores.mean(), scores.std(), labels, predicted, "none", "n/a")
    cm = confusion_matrix(labels, predicted)
    print_cm(cm, label_names)

    ## KNN
    print "\n###KNN"
    n_neighbors = [1,3]
    estimator = GridSearchCV(knn,
                             dict(n_neighbors=n_neighbors),
                             n_jobs=n_processes)
    estimator.fit(features, labels)
    scores = cross_validation.cross_val_score(estimator, features, labels, cv=folds)
    print("KNN Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std()))
    predicted = cross_validation.cross_val_predict(estimator, features, labels, cv=folds)
    cr = classification_report(labels, predicted)
    print cr
    summary.add_result("KNN", cr, scores.mean(), scores.std(), labels, predicted, estimator.best_params_, "n/a")
    cm = confusion_matrix(labels, predicted)
    print_cm(cm, label_names)

    print "\n###SVM"

    Cs = [10**-1, 1, 10, 100, 1000]
    gammas = [1e-3, 1e-4]
    estimator = GridSearchCV(svmc,
                             dict(C=Cs,
                                  gamma=gammas),
                             n_jobs=n_processes)
    estimator.fit(features, labels)
    scores = cross_validation.cross_val_score(estimator, features, labels, cv=folds)
    print("SVM Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std()))
    predicted = cross_validation.cross_val_predict(estimator, features, labels, cv=folds)
    cr = classification_report(labels, predicted)
    print cr
    summary.add_result("SVM", cr, scores.mean(), scores.std(), labels, predicted, estimator.best_params_, "n/a")
    cm = confusion_matrix(labels, predicted)
    print_cm(cm, label_names)

    print "\n@@@Feature Selection"
    print

    print "\n###NB + Anova"
    transform = SelectPercentile(f_classif)
    clf = Pipeline([('anova', transform), ('nb', nb)])
    percentiles = (np.arange(11) * 10)[1:]
    estimator = GridSearchCV(clf,
                             dict(anova__percentile=percentiles),
                             n_jobs=n_processes)
    estimator.fit(features, labels)
    best_percentile = estimator.best_estimator_.named_steps['anova'].percentile
    scores = cross_validation.cross_val_score(estimator, features, labels, cv=folds)

    anova_scores =  estimator.best_estimator_.named_steps['anova'].scores_
    sorted_anova_scores = np.argsort(anova_scores)
    sorted_anova_features = features_names[sorted_anova_scores]

    print("anova (percentile = %d) + NB Accuracy: %0.2f (+/- %0.2f)" % (best_percentile, scores.mean(), scores.std()))
    predicted = cross_validation.cross_val_predict(estimator, features, labels, cv=folds)
    cr = classification_report(labels, predicted)
    print cr
    summary.add_result("NB+Anova", cr, scores.mean(), scores.std(), labels, predicted, estimator.best_params_, sorted_anova_features)
    cm = confusion_matrix(labels, predicted)
    print_cm(cm, label_names)

    print "\n###NB + PCA"
    transform = PCA()
    clf = Pipeline([('pca', transform), ('nb', nb)])
    n_components = np.floor(np.linspace(1, features.shape[1], 10)).astype(int)
    estimator = GridSearchCV(clf,
                             dict(pca__n_components=n_components),
                             n_jobs=n_processes)
    estimator.fit(features, labels)
    best_n_components = estimator.best_estimator_.named_steps['pca'].n_components
    scores = cross_validation.cross_val_score(estimator, features, labels, cv=folds)

    print("pca (n_components = %d) + NB Accuracy: %0.2f (+/- %0.2f)" % (best_n_components, scores.mean(), scores.std()))
    predicted = cross_validation.cross_val_predict(estimator, features, labels, cv=folds)
    cr = classification_report(labels, predicted)
    print cr
    summary.add_result("NB+PCA", cr, scores.mean(), scores.std(), labels, predicted, estimator.best_params_, "PCA_COMPONENTS")
    cm = confusion_matrix(labels, predicted)
    print_cm(cm, label_names)

    print "\n###KNN + Anova"
    transform = SelectPercentile(f_classif)
    clf = Pipeline([('anova', transform), ('knn', knn)])
    percentiles = (np.arange(11) * 10)[1:]
    n_neighbors = [1,3]
    estimator = GridSearchCV(clf,
                             dict(anova__percentile=percentiles,
                                  knn__n_neighbors=n_neighbors),
                             n_jobs=n_processes)
    estimator.fit(features, labels)
    best_percentile = estimator.best_estimator_.named_steps['anova'].percentile
    scores = cross_validation.cross_val_score(estimator, features, labels, cv=folds)

    anova_scores =  estimator.best_estimator_.named_steps['anova'].scores_
    sorted_anova_scores = np.argsort(anova_scores)
    sorted_anova_features = features_names[sorted_anova_scores]

    print("anova (percentile = %d) + KNN Accuracy: %0.2f (+/- %0.2f)" % (best_percentile, scores.mean(), scores.std()))
    predicted = cross_validation.cross_val_predict(estimator, features, labels, cv=folds)
    cr = classification_report(labels, predicted)
    print cr
    summary.add_result("KNN+Anova", cr, scores.mean(), scores.std(), labels, predicted, estimator.best_params_, sorted_anova_features)
    cm = confusion_matrix(labels, predicted)
    print_cm(cm, label_names)

    print "\n###KNN + PCA"
    transform = PCA()
    clf = Pipeline([('pca', transform), ('knn', knn)])
    n_components = np.floor(np.linspace(1, features.shape[1], 10)).astype(int)
    n_neighbors = [1,3]
    estimator = GridSearchCV(clf,
                             dict(pca__n_components=n_components,
                                  knn__n_neighbors=n_neighbors),
                             n_jobs=n_processes)
    estimator.fit(features, labels)
    best_n_components = estimator.best_estimator_.named_steps['pca'].n_components
    scores = cross_validation.cross_val_score(estimator, features, labels, cv=folds)

    # print "####\n####\n####\n"
    # print estimator.best_estimator_.named_steps['pca'].components_
    # print "####\n####\n####\n"

    print("pca (n_components = %d) + KNN Accuracy: %0.2f (+/- %0.2f)" % (best_n_components, scores.mean(), scores.std()))
    predicted = cross_validation.cross_val_predict(estimator, features, labels, cv=folds)
    cr = classification_report(labels, predicted)
    print cr
    summary.add_result("KNN+PCA", cr, scores.mean(), scores.std(), labels, predicted, estimator.best_params_, "PCA_COMPONENTS")
    cm = confusion_matrix(labels, predicted)
    print_cm(cm, label_names)

    print "\n###SVM + Anova"
    transform = SelectPercentile(f_classif)
    clf = Pipeline([('anova', transform), ('svm', svmc)])
    percentiles = (np.arange(11) * 10)[1:]
    Cs = [10**-1, 1, 10, 100, 1000]
    gammas = [1e-3, 1e-4]
    estimator = GridSearchCV(clf,
                             dict(anova__percentile=percentiles,
                                  svm__gamma=gammas,
                                  svm__C=Cs),
                             n_jobs=n_processes)
    estimator.fit(features, labels)
    best_percentile = estimator.best_estimator_.named_steps['anova'].percentile
    scores = cross_validation.cross_val_score(estimator, features, labels, cv=folds)

    anova_scores =  estimator.best_estimator_.named_steps['anova'].scores_
    sorted_anova_scores = np.argsort(anova_scores)
    sorted_anova_features = features_names[sorted_anova_scores]

    print("anova (percentile = %d) + SVM Accuracy: %0.2f (+/- %0.2f)" % (best_percentile, scores.mean(), scores.std()))
    predicted = cross_validation.cross_val_predict(estimator, features, labels, cv=folds)
    cr = classification_report(labels, predicted)
    print cr
    summary.add_result("SVM+Anova", cr, scores.mean(), scores.std(), labels, predicted, estimator.best_params_, sorted_anova_features)
    cm = confusion_matrix(labels, predicted)
    print_cm(cm, label_names)

    print "\n###SVM + PCA"
    transform = PCA()
    clf = Pipeline([('pca', transform), ('svm', svmc)])
    n_components = np.floor(np.linspace(1, features.shape[1], 10)).astype(int)
    Cs = [10**-1, 1, 10, 100, 1000]
    gammas = [1e-3, 1e-4]
    estimator = GridSearchCV(clf,
                             dict(pca__n_components=n_components,
                                  svm__gamma=gammas,
                                  svm__C=Cs),
                             n_jobs=n_processes)
    estimator.fit(features, labels)
    best_n_components = estimator.best_estimator_.named_steps['pca'].n_components
    scores = cross_validation.cross_val_score(estimator, features, labels, cv=folds)

    print("pca (n_components = %d) + SVM Accuracy: %0.2f (+/- %0.2f)" % (best_n_components, scores.mean(), scores.std()))
    predicted = cross_validation.cross_val_predict(estimator, features, labels, cv=folds)
    cr = classification_report(labels, predicted)
    print cr
    summary.add_result("SVM+PCA", cr, scores.mean(), scores.std(), labels, predicted, estimator.best_params_, "PCA_COMPONENTS")
    cm = confusion_matrix(labels, predicted)
    print_cm(cm, label_names)

    return summary

def output_experiment(saidas, dataset_list_filename, classification_summary, file_prefix):
    cr_cm = open(saidas + "/" + dataset_list_filename.split(".")[0] + file_prefix + "_cr_cm.txt", "w")

    for key in sorted(classification_summary.results.keys()):
        cr_cm.write("\n")
        cr_cm.write("results for %s\n" % (key))
        cr_cm.write(classification_report(classification_summary.results[key]['labels'], classification_summary.results[key]['predicted']))
        cm = confusion_matrix(classification_summary.results[key]['labels'], classification_summary.results[key]['predicted'])
        cr_cm.write("\nconfusion matrix:\n")
        print_cm(cm, classification_summary.label_names, file=cr_cm)

    classification_summary.to_csv(saidas + "/" + dataset_list_filename.split(".")[0] + file_prefix + ".csv")
    cr_cm.close()

if __name__ == "__main__":

    classification_summary = train_and_classify("csv/genres/genres_tza_one_band_tex.csv")
    output_experiment(".", "gtzan_small2.txt", classification_summary, "tzanetakis")







