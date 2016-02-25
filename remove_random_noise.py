import numpy as np
import matplotlib.pyplot as plt
import mir3.modules.tool.wav2spectrogram as wav2spec

eps = np.finfo(float).eps

def inDb(a):
    return 20 * np.log10(a + eps)

def saveBMP(data, filename):
    pass

def remove_random_noise(spectrogram, plot=False, outputPngName=None, filter_compensation='log10', passes=1):
    nxMx = spectrogram.data

    nxMx = nxMx / np.max(np.abs(nxMx))

    means = np.mean(nxMx, axis=1)
    stdevs = np.std(nxMx, axis=1)

    fs = spectrogram.metadata.sampling_configuration.fs
    H = spectrogram.metadata.sampling_configuration.window_step
    N = spectrogram.metadata.sampling_configuration.dft_length
    freq_per_bin = fs / len(means)

    frmTime = H * np.arange(nxMx.shape[1])/float(fs)
    binFreq = freq_per_bin*np.arange(len(means)) * 0.5

    if plot:
        plt.figure(1)
        plt.subplot(311)
        plt.pcolormesh(frmTime, binFreq, inDb(nxMx))
        plt.colormaps()

    low = np.min(nxMx)

    nf_nxMx = np.copy(nxMx)
    nf_nxMx2 = np.copy(nxMx)

    maxlog = np.log10(len(means))

    subs = []

    if filter_compensation == 'log10':
        for i in range(len(means)):
            if i == 0:
                continue
            subs.append(1 - (np.log10(i) / maxlog))

            for k in range(passes):
                nf_nxMx[i] -= abs(means[i] + ((1 - (np.log10(i + eps) / maxlog)) * stdevs[i]))
                nf_nxMx2[i] -= abs(means[i] + ((1 * (np.log10(i + eps) / maxlog)) * stdevs[i]))

    if filter_compensation == 'linear':
        for i in range(len(means)):
            nf_nxMx[i] -= abs(means[i] + ( (1 - (i / len(means)-1)) * stdevs[i]))

    nf_nxMx = np.clip(nf_nxMx, a_min=low, a_max=1.0)
    nf_nxMx2 = np.clip(nf_nxMx2, a_min=low, a_max=1.0)

    if plot:

        # plt.figure(0)
        # plt.plot(subs)
        # plt.figure(1)

        plt.subplot(312)
        plt.pcolormesh(frmTime,
        binFreq,
        inDb(nf_nxMx))

        plt.subplot(313)
        plt.pcolormesh(frmTime,
        binFreq,
        inDb(nf_nxMx2))

    if outputPngName is not None:
        f = plt.figure(2)
        plt.pcolormesh(frmTime, binFreq,inDb(nf_nxMx))
        plt.axis('off')
        plt.savefig(outputPngName, bbox_inches='tight', pad_inches=0, dpi=300)

    if plot:
        plt.figure(1)
        plt.show(1)

    plt.close()

    spectrogram.data = nf_nxMx


def remove_random_noise_from_wav(filename, plot=False, outputPngName=None, filter_compensation='log10', passes=1):

    audio_file = open(filename, 'rb')
    spec = wav2spec.Wav2Spectrogram().convert(audio_file, dft_length=2048,\
                                                              window_step=1024,\
                                                              window_length=2047)
    remove_random_noise(spec, plot=plot, outputPngName=outputPngName, filter_compensation=filter_compensation, passes=passes)

    audio_file.close()

if __name__ == "__main__":

    #filename = "/home/juliano/Music/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN29603.wav"
    filename = "/home/juliano/Music/genres_wav/rock.00000.wav"

    #filename = "/home/juliano/birds/BAND_TAILED_NIGHTHAWK/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN11254.wav"
    #filename = "/home/juliano/birds/BAND_TAILED_NIGHTHAWK/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN15299.wav"
    #filename = "/home/juliano/birds/BAND_TAILED_NIGHTHAWK/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN25674.wav"
    #filename = "/home/juliano/base_teste_rafael_94_especies/BAY_WREN/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN19798.wav"
    #filename = "/home/juliano/base_teste_rafael_94_especies/BAY_WREN/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN29607.wav"
    #filename = "/home/juliano/base_teste_rafael_94_especies/BAY_WREN/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN29358.wav"
    #filename = "/home/juliano/base_teste_rafael_94_especies/BAY_WREN/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN17844.wav"
    #filename = "/home/juliano/base_teste_rafael_94_especies/BAY_WREN/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN24787.wav"

    #filename = "/home/juliano/base_teste_rafael_94_especies/BUFF_NECKED_IBIS/LIFECLEF2014_BIRDAMAZON_XC_WAV_RN929.wav"
    #filename = "/home/juliano/base_teste_rafael_94_especies/BUFF_NECKED_IBIS/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN26407.wav"

    #filename = "/home/juliano/birds/MARSH_TAPACULO/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN17091.wav"
    #filename = "/home/juliano/birds/MARSH_TAPACULO/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN21923.wav"
    #filename = "/home/juliano/birds/MARSH_TAPACULO/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN23448.wav"
    #filename = "/home/juliano/birds/MARSH_TAPACULO/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN25278.wav"
    #filename = "/home/juliano/birds/MARSH_TAPACULO/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN30281.wav"

    #(fs, x) = scipy.io.wavfile.read(filename)

    #(fs, x) = UF.wavread("/home/juliano/Music/genres_wav/rock.00000.wav")

    remove_random_noise_from_wav(filename, True, 'foo.png', filter_compensation='log10', passes=3)



