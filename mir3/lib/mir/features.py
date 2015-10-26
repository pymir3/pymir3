import numpy

"""Feature extraction algorithms

Will extract features from a spectrogram.
The spectrogram is expected to be a Freq (lines) x Frames (cols)
numpy array. All results will be in terms of this scale. For good results,
it is necessary to previously remove the second half of the DFT (the
symmetrical part).
"""

def flatness(A):
    """Spectral flatness of each frame"""
    return numpy.exp(  numpy.mean(numpy.log(numpy.maximum(A, 0.0001)), 0) ) / \
        (numpy.mean(A, 0) + (10**(-6)))

def energy(A):
    """Energy of each frame"""
    return numpy.sum(A**2 , 0)

def flux(A):
    """Spectral flux of each frame"""
    a = numpy.diff(A, axis = 1)
    s = numpy.sum(numpy.maximum(a, 0), axis=0)
    s0 = numpy.sum(A, axis=0) + (10**(-6))
    return numpy.hstack ((numpy.array([0]), s))/s0


def centroid(A):
    """Centroid of each frame"""
    lin = A.shape[0]
    col = A.shape[1]

    return numpy.sum( A * \
            numpy.transpose(numpy.tile(numpy.arange(lin), (col,1))), 0)\
            / numpy.maximum(0.00001, numpy.sum(A, 0))

def rolloff(A, alpha=0.95):
    """Rolloff of each frame"""
    return numpy.sum ( (numpy.cumsum(A, 0)/\
                        numpy.maximum(0.0000001, numpy.sum(A, 0))) < alpha, 0)


