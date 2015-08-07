import numpy

"""Feature extraction algorithms

Will extract features from a time-domain signal
"""

def zero_crossings(wav_data, frame_length, window_size):
    """Calculates the Time Domain Zero Crossings feature as in (Tzanetakis, 2002)"""
    
    def sign(n):
        return 1 if n>=0 else 0
        
    f = numpy.vectorize(sign, otypes=[int])
    
    wav_data = f(wav_data)
    begin = 1
    limit = len(wav_data)
    
    ret = numpy.array(())
    while begin <= limit:
        end = min((begin + frame_length - 1),limit)
        k = numpy.array((numpy.sum(numpy.abs(numpy.diff(wav_data[begin:end])), dtype=float)))
        k/=2
        ret = numpy.hstack((ret, k))
        begin += window_size
    
    print ret
    
    return ret
