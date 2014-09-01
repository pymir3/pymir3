import numpy
import numpy.linalg


def distance_sum(inputs, references):
    """Sum of all distances between inputs and references

    Each element should be in a row!
    """
    norms = numpy.zeros(inputs.shape[0])
    for i in xrange(references.shape[0]):
        norms += numpy.apply_along_axis(numpy.linalg.norm, 1,
                                    inputs-references[i,:])

    return norms

def distance_min(inputs, references):
    """Minimum distances between inputs and any reference

    Each element should be in a row!
    """
    norms = numpy.ones(inputs.shape[0])*99999999
    for i in xrange(references.shape[0]):
        norms = numpy.minimum(norms,
                              numpy.apply_along_axis(numpy.linalg.norm, 1,
                                    inputs-references[i,:]))

    return norms

def distance_matrix(inputs):
    """Returns a distance matrix
    """
    D = numpy.ones( (inputs.shape[0], inputs.shape[0]) )*99999999
    for i in xrange(inputs.shape[0]):
        for j in xrange(i):
            D[i,j] = numpy.linalg.norm(inputs[i,:]-inputs[j,:])
            D[j,i] = numpy.linalg.norm(inputs[i,:]-inputs[j,:])
    return D

def distance_mutual_min(inputs, references):
    """Distance using a mutual distance reference
    
    Inspired in:
    USING MUTUAL PROXIMITY TO IMPROVE CONTENT-BASED AUDIO SIMILARITY
    Dominik Schnitzer, Arthur Flexer, Markus Sched, Gerhard Widmer
    """
    d = distance_matrix(inputs)
    a = distance_min(inputs, references)
    for i in xrange(len(a)):
        a[i] = a[i] - numpy.min(d[:,i])

    return a


def range_distance(inputs, references):
    """Minimum distance from boundaries of a rang
    """
    mi = numpy.amin(references, 0)
    ma = numpy.amax(references, 0)
    norms = numpy.zeros(inputs.shape[0])

    for i in xrange(inputs.shape[0]):
        for j in xrange(inputs.shape[1]):
            if (inputs[i,j] < mi[j]) or \
                 (inputs[i,j] > ma[j]):
                norms[i] += numpy.min([abs(inputs[i,j]-mi[j]),\
                                       abs(inputs[i,j]-ma[j])])**2
        norms[i] = norms[i]**(0.5)
    return norms

def mutual_range_distance(inputs, references):
    """Minimum distance from boundaries of a range
    """
    mi = numpy.amin(references, 0)
    ma = numpy.amax(references, 0)
    norms = numpy.zeros(inputs.shape[0])
    d = distance_matrix(inputs)

    for i in xrange(inputs.shape[0]):
        for j in xrange(inputs.shape[1]):
            if (inputs[i,j] < mi[j]) or \
                 (inputs[i,j] > ma[j]):
                norms[i] += numpy.min([abs(inputs[i,j]-mi[j]),\
                                       abs(inputs[i,j]-ma[j])])**2
        norms[i] = norms[i]**(0.5)
        norms[i] = norms[i] - numpy.min(d[:,i])
    return norms
            
#a = numpy.array([[2, 4, 6], [4, 3, 2], [5, -2, -1], [10, 11, 12], [15, 20, 31]])
#b = numpy.array([[10, 11, 12], [-1, -2, -3]])
#print distance_sum(a, b)
#print a
#print b
#print distance_min(a, b)
#print distance_mutual_min(a, b)
