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
    
    ret = numpy.array(())
    for k in range ((len(wav_data)/window_size) - 1):
        this_start = k* window_size
        this_end = this_start + frame_length
        k = numpy.array((numpy.sum(numpy.abs(numpy.diff(wav_data[this_start:this_end])), dtype=float)))
        k/=2
        ret = numpy.hstack((ret, k))
    
    return ret
