import sys
import numpy as np
sys.path.append("/home/juliano/Dropbox/Doutorado/MIR/curso_aspma/sms-tools-master/software/models")
import stft
import utilFunctions as UF
from scipy.signal import get_window
import matplotlib.pyplot as plt

import mir3.modules.tool.wav2spectrogram as wav2spec

eps = np.finfo(float).eps

def inDb(a):
    return 20 * np.log10(a + eps)

def saveBMP(data, filename):
    pass

if __name__ == "__main__":

    #filename = "/home/juliano/Music/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN29603.wav"
    #filename = "/home/juliano/Music/genres_wav/rock.00000.wav"

    #filename = "/home/juliano/birds/BAND_TAILED_NIGHTHAWK/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN11254.wav"
    filename = "/home/juliano/birds/BAND_TAILED_NIGHTHAWK/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN15299.wav"

    #filename = "/home/juliano/birds/MARSH_TAPACULO/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN17091.wav"
    #filename = "/home/juliano/birds/MARSH_TAPACULO/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN21923.wav"
    #filename = "/home/juliano/birds/MARSH_TAPACULO/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN23448.wav"
    #(fs, x) = scipy.io.wavfile.read(filename)

    #(fs, x) = UF.wavread("/home/juliano/Music/genres_wav/rock.00000.wav")

    audio_file = open(filename, 'rb')
    spec = wav2spec.Wav2Spectrogram().convert(audio_file, dft_length=2048,\
                                                              window_step=1024,\
                                                              window_length=2047)
    nxMx = spec.data

    #print nxMx

    plt.figure(1)
    plt.subplot(211)
    plt.pcolormesh(inDb(nxMx))
    plt.colormaps()

    nxMx = nxMx / np.max(np.abs(nxMx))

    low = np.min(nxMx)

    print "low", low

    means = np.mean(nxMx, axis=1)
    stdevs = np.std(nxMx, axis=1)

    #nf_nxMx = nxMx -  0.025

    nf_nxMx = np.copy(nxMx)

    print means

    for i in range(len(means)):
        for k in range(nxMx.shape[1]):
            nf_nxMx[i][k] -= abs(means[i] + (2 * stdevs[i]))

    nf_nxMx = np.clip(nf_nxMx, a_min=low, a_max=1.0)

    plt.subplot(212)
    plt.pcolormesh(inDb(nf_nxMx))


    f = plt.figure(2)
    plt.pcolormesh(inDb(nf_nxMx))
    plt.axis('off')
    plt.savefig('foo.png', bbox_inches='tight', pad_inches=0, dpi=300)

    # f = plt.figure(2)
    # plt.pcolormesh(inDb(nf_nxMx))
    # plt.gcf().canvas.draw()
    # pixels = plt.gcf().canvas.print_to_buffer()

    plt.figure(1)
    plt.show(1)

    #y = stft.stftSynth(nf_nxMx, xPx, M, H)

    #UF.wavwrite(y, fs, "test.wav")



