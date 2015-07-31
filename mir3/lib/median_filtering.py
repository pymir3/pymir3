import numpy
import numpy.linalg

def median_filter(x, window_length=5):
    """Applies a median filter to each column of the input.

    output[n] = median of input[n:n+window_length]
    """
    output = numpy.zeros( (x.shape[0]-window_length, \
                           x.shape[1]) )
    for T in xrange(output.shape[0]):
        output[T, :] = numpy.median(x[T:T+window_length, :], axis=0)

    return output

def median_filter_centered(x, window_length=2):
    """Applies a median filter to each column of the input.

    output[n] = median of input[n-window_length:n+window_length]
    """
    output = numpy.zeros( (x.shape[0]-window_length, \
                           x.shape[1]) )

    for T in xrange(output.shape[0]):
        first = max(0, T-window_length)
        last = min(x.shape[0], T+window_length)
        output[T, :] = numpy.median(x[first:last, :],\
                            axis=0)

    return output
