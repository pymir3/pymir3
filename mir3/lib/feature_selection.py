import numpy
import numpy.linalg
import scipy.stats


def minimum_variance(data, n_features=1):
    """Selects features that have minimum variance
    """
    variances = numpy.maximum(0.001, numpy.apply_along_axis(numpy.var, 0, data))
    
    mask = numpy.zeros(variances.shape)
    for n in xrange(n_features):
        p = numpy.argmin(variances)
        mask[p] = 1
        variances[p] = numpy.max(variances)

    return mask

def minimum_variance_rel(training_set, all_data, n_features=1):
    """Selects features that have minimum relative variance

    training_set - small set you want to isolate from data1
    all_data - big set with all your data
    n_features - number of features you want to select
    """
    
    variances0 = numpy.maximum(0.001, numpy.apply_along_axis(numpy.var, 0, training_set))
    variances1 = numpy.maximum(0.001, numpy.apply_along_axis(numpy.var, 0, all_data))
    variances = variances0 / variances1
    
    mask = numpy.zeros(variances.shape)
    for n in xrange(n_features):
        p = numpy.argmin(variances)
        mask[p] = 1
        variances[p] = numpy.max(variances)

    return mask

def sum_cluster_distance(cluster1, cluster2):
    """Returns the sum of distances between elements of clusters
    """
    D = 0.0
    for i in xrange(cluster1.shape[0]):
        for j in xrange(cluster2.shape[0]):
            D = D + numpy.linalg.norm(cluster1[i,:]-cluster2[j,:])
    return D

def selection_by_correlation(cluster1, cluster2, n_features=1):
    """Masks n_features that are most correlated with the classification
    """
    mask = numpy.zeros(cluster1.shape[1])
    corr = numpy.zeros(cluster1.shape[1])

    groups = numpy.vstack( (
            numpy.zeros( (cluster1.shape[0], 1)),
            numpy.ones( (cluster2.shape[0], 1))
            ))

    data = numpy.vstack( (cluster1, cluster2) )
    
    for i in xrange(cluster1.shape[1]):
        corr[i] = abs(scipy.stats.pearsonr(data[:,i], groups[:,0].T)[0])

    for j in xrange(n_features):
        k = numpy.argmax(corr)
        corr[k] = 0
        mask[k] = 1

    return mask


# print "Arrays:"
# a = numpy.array([[2, 4, 6], [4, 3, 2], [5, -2, -1], [10, 11, 12], [15, 20, 31]])
# b = numpy.array([[10, 11, 12], [-1, -2, -3]])
# print a
# print numpy.maximum(0.001, numpy.apply_along_axis(numpy.var, 0, a))
# print b
# print numpy.maximum(0.001, numpy.apply_along_axis(numpy.var, 0, b))

# print "Minimum variance:"
# mask = minimum_variance(b, 2)
# print mask
# print a * mask.reshape(1, -1)

# print "Minimum variance_rel:"
# mask = minimum_variance_rel(b, a, 2)
# print mask
# print a * mask.reshape(1, -1)

