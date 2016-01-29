# Audio Feature Extraction functions


import numpy as np

#import mir3.modules.features as feat
import mir3.lib.mir.features as mir
import mir3.modules.features.filterbank as fbank
import mir3.modules.tool.wav2spectrogram as wav2spec
import mir3.data.spectrogram as spec
import mir3.data.feature_track as track

def audio_feature_extraction(filename_in, frame_len=1024, frame_step=512):
    """Extracts features from an audio file.

    Inputs:
    filename_in - string containing filename from which the features will be
    extracted
    frame_len and frame_step - frame length and step between frames (in samples)
    for the framewise feature processing

    Outputs:
    numpy array in which each column represents a different feature and each
    line represents the corresponding frame in the audio file.
    """

    # Open audio file
    audio_file = open(filename_in, 'rb')
    w_spec = wav2spec.Wav2Spectrogram()
    s = w_spec.convert(audio_file, window_length=frame_len,\
                            window_step=frame_step)
    audio_file.close()

    # Hand-made features
    flatness = mir.flatness(s.data)
    energy = mir.energy(s.data)
    flux = mir.flux(s.data)
    centroid = mir.centroid(s.data)
    rolloff = mir.rolloff(s.data)
    low_energy = mir.rolloff(s.data, 10)

    flatness.shape = (flatness.shape[0],1)
    energy.shape = (energy.shape[0],1)
    flux.shape = (flux.shape[0], 1)
    centroid.shape = (centroid.shape[0],1)
    rolloff.shape = (rolloff.shape[0],1)
    low_energy.shape = (low_energy.shape[0],1)


    # Filterbank with triangular frequencies
    f = fbank.FilterBank()
    frequency = 10.0
    central_frequencies = []
    while frequency < (s.metadata.sampling_configuration.fs)/2:
        central_frequencies.append(float(frequency))
        frequency *= 1.5 # Tune this at will.
                         # Values <= 1 will break the system.
    H = f.build_filterbank(central_frequencies, s)
    filterbank_out = np.dot(H, s.data).T

    #print flatness.shape, energy.shape, flux.shape, centroid.shape,\
    #        rolloff.shape, low_energy.shape
    #print filterbank_out.shape
    #print s.data.T.shape


    all_features = np.hstack( (flatness, energy, flux, centroid, rolloff,\
        low_energy, filterbank_out, s.data.T) )

    return all_features

if __name__ == "__main__":
    import sys
    import time

    if len(sys.argv)==1:
        print "Usage: python " + sys.argv[0] + " <wav_file>"
        exit()


    T0 = time.time()
    feat = audio_feature_extraction(sys.argv[1])
    T1 = time.time()
    #print "Feature extraction took ", T1-T0, " seconds"

    if len(sys.argv)==2:
        exit()

    if sys.argv[2] == '-v':


        for i in xrange(feat.shape[0]):
            line=""
            for j in xrange(feat.shape[1]-1):
                line += str(feat[i,j]) + ", "
            line += str(feat[i,-1]) + "\n"
            print line



