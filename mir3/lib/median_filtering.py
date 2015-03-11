import numpy
import numpy.linalg

def median_filter(input, window_length=5):
    """Applies a median filter to each column of the input.

    output[n] = median of input[n:n+window_length]
    """
    output = numpy.zeros( (input.shape[0]-window_length, \
                           input.shape[1]) )
    for T in xrange(output.shape[0]):
        output[T, :] = numpy.median(input[T:T+window_length, :], axis=0)

    return output
