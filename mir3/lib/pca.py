import numpy
import numpy.linalg

def PCA(data, n_bases=None, scale=None, compute_reduced=True,
        compute_base=True, compute_mean=False):
    """Computes the PCA of a given data.

    Either 'n_bases' or 'scale' must be provided so that the number of basis can
    be chosen. The algorithm only uses 'n_bases' if 'scale' is None. In case
    both of them are None, an exception is raised.

    The first two flags indicate whether to compute the reduced data and the
    base, as not always both information will be necessary. If 'compute_reduced'
    is False, then the returned 'base_trunc' is None. The same occurs for
    'compute_base' and 'base_trunc'. The last flag indicates whether to take the
    mean out of the data. This is the "correct" approach, but then 3 variables
    are needed to rebuild the data. In case of a linear decomposition, the flag
    should be False so that the decomposition only have 2 terms.

    The reduction occurs on the columns, that is, the returned data has less
    columns than the original one.

    The results should provide data_trunc == numpy.dot(data, base_trunc). The
    approximation of the original data can be reconstructed with:
    data2 = numpy.dot(data_trunc, base_trunc.transpose())
    data2 += data_mean.reshape((-1, 1))

    Args:
        data: the data used to compute PCA.
        n_bases: number of bases to keep.
        scale: amount of energy to keep.
        compute_reduced: flag to compute the reduced form of the data.
        compute_base: flag to compute the base of the data.
        compute_mean: whether the original data should have its mean taken off.

    Returns:
        Tuple of (data truncated, base_truncated, data median).

    Raises:
        ValueError: neither 'n_bases' or 'scale' was provided.
    """
    if compute_mean:
        data_mean = numpy.mean(data, 0)
        data_clean = (data - data_mean)
    else:
        data_clean = data
        data_mean = numpy.zeros((data.shape[0],))

    u, s, v = numpy.linalg.svd(data_clean, full_matrices=False)

    if scale is not None:
        energy = numpy.cumsum(s)/numpy.sum(s)
        index = numpy.where(energy >= scale)[0][0]+1
    elif n_bases is not None:
        index = n_bases
    else:
        raise ValueError("One of 'scale' or 'n_bases' must be not None")

    if compute_reduced:
        s_trunc = s[0:index]
        u_trunc = u[:,0:index]
        data_trunc = numpy.dot(u_trunc, numpy.diag(s_trunc))
    else:
        data_trunc = None

    if compute_base:
        base_trunc = v.transpose()[:,0:index]
    else:
        base_trunc = None

    # This works even though the data didn't had its mean removed. Maybe the
    # base already has this? TODO: check if it makes sense
    #print numpy.allclose(data_trunc, numpy.dot(data, base_trunc))

    return data_trunc, base_trunc, data_mean


def subset_PCA(all_data, training_data):
    """Computes the PCA using training data and applies the transformation to all_data
    """
    t, b, m = PCA(training_data, n_bases=training_data.shape[0],
                  compute_mean=False)

    orthogonal_data = numpy.dot(all_data, b)

    return orthogonal_data, t

def normalize(data):
    """Normalizes each row to unitary norm
    """
    norms = numpy.apply_along_axis(numpy.linalg.norm, 1, data)
    return data / norms.reshape(-1,1)


def orthogonal_projection(all_data, training_data):
    """Projection norm of all_data over space defined by training_data

    """
    o, t = subset_PCA(normalize(all_data), normalize(training_data))
    norms = numpy.apply_along_axis(numpy.linalg.norm, 1, o)
    return norms, o, t

#a = numpy.array([[2, 4, 6], [4, 3, 2], [5, -2, -1], [10, 11, 12], [15, 20, 31]])
#b = numpy.array([[10, 11, 12], [-1, -2, -3]])
#n, o, t = orthogonal_projection(a, b)
#print o
#print t
#print n
