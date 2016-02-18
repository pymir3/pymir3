import numpy as np
from sklearn import cross_validation
from sklearn import neighbors
from sklearn import svm
from sklearn.feature_selection import SelectPercentile
from sklearn.feature_selection import f_regression
from sklearn.feature_selection import f_classif
from sklearn.pipeline import Pipeline

if __name__ == "__main__":

    ### bands
    csv = np.genfromtxt("dataset_features.csv", dtype='string' ,skip_header=1, delimiter=',')

    features = np.asfarray(csv.T[:-1].T)
    labels =  csv.T[-1:].T
    labels.shape = (labels.shape[0])

    #classifiers
    knn = neighbors.KNeighborsClassifier(n_neighbors=1)
    svmc = svm.SVC(kernel='rbf', C=5)

    print "all features"

    scores = cross_validation.cross_val_score(knn, features, labels, cv=10)
    print("KNN Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std()))

    scores = cross_validation.cross_val_score(svmc, features, labels, cv=10)
    print("SVM Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std()))

    print "anova feature selection"

    #http://scikit-learn.org/stable/auto_examples/svm/plot_svm_anova.html (isso tem um exemplo legal)

    #transform = SelectPercentile(f_classif)
    #clf = Pipeline([('anova', transform), ('svc', svm.SVC(C=500))])




    # anova_filter = SelectPercentile(f_regression, percentile=30)
    # anova_svm = Pipeline([('anova', anova_filter), ('svc', svmc)])
    #
    # anova_svm.set_params(anova__percentile=10, svc__C=500)
    #
    # scores = cross_validation.cross_val_score(anova_svm, features, labels, cv=10)
    # print("SVM Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std()))





