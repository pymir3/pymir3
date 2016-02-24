import numpy as np
from sklearn import cross_validation
from sklearn import neighbors
from sklearn import svm
from sklearn.feature_selection import SelectPercentile
from sklearn.feature_selection import f_regression
from sklearn.feature_selection import f_classif
from sklearn.decomposition import PCA
from sklearn.decomposition import RandomizedPCA
from sklearn.decomposition import KernelPCA
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV

if __name__ == "__main__":

    do_anova = True
    do_pca = True

    ### bands
    csv = np.genfromtxt("birdclef_tza_bands.csv", dtype='string' ,skip_header=1, delimiter=',')

    features = np.asfarray(csv.T[:-1].T)
    labels =  csv.T[-1:].T
    labels.shape = (labels.shape[0])

    #classifiers
    knn = neighbors.KNeighborsClassifier(n_neighbors=1)
    svmc = svm.SVC(kernel='rbf', C=300)

    print "all features"

    scores = cross_validation.cross_val_score(knn, features, labels, cv=10)
    print("KNN Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std()))

    scores = cross_validation.cross_val_score(svmc, features, labels, cv=10)
    print("SVM Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std()))

    print "\nfeature selection"

    #http://scikit-learn.org/stable/auto_examples/svm/plot_svm_anova.html (isso tem um exemplo legal)

    if do_anova:
        transform = SelectPercentile(f_classif)
        clf = Pipeline([('anova', transform), ('svc', svm.SVC(C=300))])
        clf.set_params(anova__percentile=70)
        scores = cross_validation.cross_val_score(clf, features, labels)

        print("anova + SVM Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std()))


    if do_pca:
        transform = PCA()
        clf = Pipeline([('pca', transform), ('svc', svm.SVC(C=300))])
        n_components = [20, 30, 40, 50, 60, 70, 100, 120, 130, 150]
        estimator = GridSearchCV(clf,
                             dict(pca__n_components=n_components))
        estimator.fit(features, labels)

        best_ncomponents = estimator.best_estimator_.named_steps['pca'].n_components
        clf.set_params(pca__n_components=best_ncomponents)
        scores = cross_validation.cross_val_score(clf, features, labels)

        print("PCA (n_components = %d)  + SVM Accuracy: %0.2f (+/- %0.2f)" % (best_ncomponents, scores.mean(), scores.std()))







