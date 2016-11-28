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

def RMSEnergy(A):
    """RMS Energy of each Frame"""
    return  numpy.sqrt( (1.0 / A.shape[0]) * numpy.sum(A**2, axis=0))

def flux(A):
    """Spectral flux of each frame"""
    a = numpy.diff(A, axis = 1)
    s = numpy.sum(numpy.maximum(a, 0), axis=0)
    s0 = numpy.sum(A, axis=0) + (10**(-6))
    return numpy.hstack ((numpy.array([0]), s))/numpy.maximum(s0, 0.0000001)



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

def low_energy(A, texture_length):
    """Low energy feature for each texture window"""
    energy_ = numpy.concatenate( (numpy.arange(1),  RMSEnergy(A) ))

    step = texture_length
    total_aw = len(energy_)
    begin = 1
    end = begin + step - 1
    
    ret = numpy.zeros( total_aw - step + 1)

    running_sum = numpy.sum( energy_[:end] )

    while end < total_aw:
        running_sum = running_sum - energy_[begin-1] + energy_[end]
        avg_energy = running_sum / step

        above_average = len ( numpy.where(energy_[begin:end] > avg_energy )[0] )

        pct = above_average / float(step)
        
        ret[begin] = pct
        
        begin+=1
        end+=1

    ret = ret[1:]

    return ret

# def low_energy(A, texture_length):
#     """Low energy feature for each texture window"""
#     energy_ = energy(A)
#     step = texture_length
#     total_aw = len(energy_)
#     begin = 0
#     end = begin + step - 1
#     ret = numpy.array(())

#     while end < total_aw:
#         avg_energy = numpy.mean(energy_[begin:end+1])
#         above_average = 0
#         for i in range(begin, end+1):
#             if energy_[i] > avg_energy:
#                 above_average += 1
#         pct = above_average / float(step)
#         ret = numpy.hstack((ret, pct))
#         begin+=1
#         end+=1

#     return ret

