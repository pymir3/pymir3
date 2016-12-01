import numpy

"""Feature extraction algorithms

Will extract features from a time-domain signal
"""

def zero_crossings(wav_data, frame_length, window_size):
    """Calculates the Time Domain Zero Crossings feature as in (Tzanetakis, 2002)"""

    def sign(n):
        return 1 if n>=0 else 0

    f = numpy.sign #numpy.vectorize(sign, otypes=[int])

    wav_data = f(wav_data)
    wav_data[wav_data == 0] = 1
    wav_data[wav_data == -1] = 0



    size = 1 + int((len(wav_data) - frame_length) / float(window_size))

    #size = int(((len(wav_data) -\
    #    (frame_length-window_size))/float(window_size))) - 1
    ret = numpy.zeros(size + 2)

    for k in xrange (size):
        this_start = k* window_size
        this_end = min(this_start + frame_length, len(wav_data))
        zc = numpy.array((numpy.sum(numpy.abs(numpy.diff(wav_data[this_start:this_end])), dtype=float)))
        zc/=2
        ret[k] = zc

    return ret


# def zero_crossings(wav_data, frame_length, window_size):
#     """Calculates the Time Domain Zero Crossings feature as in (Tzanetakis, 2002)"""

#     def sign(n):
#         return 1 if n>=0 else 0

#     f = numpy.vectorize(sign, otypes=[int])

#     wav_data = f(wav_data)

#     ret = numpy.array(())
#     for k in range ((len(wav_data)/window_size) - 1):
#         this_start = k* window_size
#         this_end = this_start + frame_length
#         k = numpy.array((numpy.sum(numpy.abs(numpy.diff(wav_data[this_start:this_end])), dtype=float)))
#         k/=2
#         ret = numpy.hstack((ret, k))

#     return ret
