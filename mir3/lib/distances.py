import numpy
import numpy.linalg
from naive_bayes import gaussian

def distance_matrix(data):
    """Returns a matrix with the Euclidean distance between each data line
    """
    D = numpy.zeros( (data.shape[0], data.shape[0]) )
    for i in xrange(data.shape[0]):
        for j in xrange(i):
            D[i,j] = numpy.linalg.norm(data[i,:]-data[j,:])
            D[j,i] = D[i,j]

    return D



def mutual_proximity(distance_matrix):
    """Returns the mutual proximity matrix given a distance matrix

    Please, see:
    USING MUTUAL PROXIMITY TO IMPROVE CONTENT-BASED AUDIO SIMILARITY
    Dominik Schnitzer, Arthur Flexer, Markus Schedl, Gerhard Widmer
    Proceedings of the 12th ISMIR (2011)
    """
    vars = numpy.var(distance_matrix, axis = 0)
    means = numpy.mean(distance_matrix, axis = 0)
    D = numpy.zeros (distance_matrix.shape)
    for i in xrange(distance_matrix.shape[0]):
        for j in xrange(i):
            D[i,j] = \
                (1 - gaussian(distance_matrix[i,j], means[i], vars[i])) * \
                (1 - gaussian(distance_matrix[i,j], means[j], vars[j]))
            D[j,i] = D[i,j]
    return D

def minimum_subset_distance(D, limits1, limits2):
    """Returns minimum distance between elements of different subsets
    """
    score = numpy.ones( (limits1[1]) )
    for i in xrange(limits1[1]):
        for j in xrange(limits2[1]-limits2[0]):
            score[i] = min(score[i], D[i,j+limits2[0]-1])
            #print i, j, D[i,j+limits2[0]-1], score[i], min(score[i], D[i,j+limits2[0]-1])
    return score

def group_subset_distance(D, limits1, limits2):
    """Returns group distance between elements of different subsets
    """
    score = numpy.ones( (limits1[1]) )
    for i in xrange(limits1[1]):
        for j in xrange(limits2[1]-limits2[0]):
            score[i] = score[i] * D[i,j+limits2[0]-1]
            #print i, j, D[i,j+limits2[0]-1], score[i], min(score[i], D[i,j+limits2[0]-1])
    return score

#A = numpy.array( [[1, 2, 3], [3, 2, 1], [0, 0, 0]] )
#D = distance_matrix(A)
#print D
#D0 = mutual_proximity(D)
#print D0
