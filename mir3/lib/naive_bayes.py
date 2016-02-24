import numpy
import numpy.linalg

def training(inputs, minvar=0.1):
    """Trains a naive-bayes classifier using inputs

    Returns means and variances of the classifiers
    """
    return numpy.mean(inputs, axis=0), numpy.maximum(minvar, numpy.var(inputs, axis=0))

def gaussian(input, mu, sigma2):
    """Calculates gaussian value for each input in the array
    """
    return (1/ (2*numpy.sqrt(3.14*sigma2))) * \
        numpy.exp( - ((input-mu)**2)/(2*sigma2))

def likelihood(inputs, means, variances):
    """Minimum distances between inputs and any reference

    Each element should be in a row!
    """
    out = numpy.ones(inputs.shape[0])
    for j in xrange(inputs.shape[1]):
        if variances[j] != 0:
            out = out * \
            (gaussian (inputs[:,j], means[j], variances[j]))

    return out

def naive_bayes(test, train):
    """Implements the whole naive bayes flow.

    Returns a likelihood array
    """
    m, v = training(train)
    return likelihood(test, m, v)

def naive_bayes_multidimensional(test, train):
    """Naive bayes analysis keeping dimensions isolated
    """
    m, v = training(train)
    out = numpy.ones( (test.shape) )
    for i in xrange(test.shape[0]):
        for j in xrange(test.shape[1]):
            out[i,j] = out[i,j] * \
            (gaussian (test[i,j], m[j], v[j]))
    return out

# a = numpy.array([[2, 4, 6], [4, 3, 2], [5, -2, -1], [10, 11, 12], [15, 20, 31]])
# b = numpy.array([[2, 4, 2], [4, 3, 1.5]])
# m, v = training(b)
# print m, v
# print likelihood(a, m, v)
# out = naive_bayes_multidimensional(a, b)
# out = (out / numpy.max(out)) * (out > 0.01)
# print out
