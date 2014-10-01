import numpy
import numpy.linalg
import scipy.stats

# Self Similarity Calculations
# Inputs:
# Feature tracks (i, j): i observations of j features
# Configuration parameters
# 
# Outputs:
# Self-Similarity Matrix S(a,b) = similarity between a and b
#

def self_similarity_euclidean(features):
    dimension = features.shape[0]
    ssm = numpy.zeros( (dimension, dimension) )
    for i in xrange(dimension):
        for j in xrange(i):
            similarity = numpy.linalg.norm(features[i,:] - features[j,:])
            ssm[i,j] = similarity
            ssm[j,i] = ssm[i,j]

    return ssm
