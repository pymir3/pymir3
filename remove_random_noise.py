import numpy as np
import matplotlib.pyplot as plt
import mir3.modules.tool.wav2spectrogram as wav2spec
import mir3.modules.features.energy as feat_energy
import mir3.modules.features.flux as feat_flux
import mir3.modules.features.centroid as feat_centroid
import mir3.modules.features.rolloff as feat_rolloff
import bandwise_features as bf

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

    if filter_compensation == 'linear':
        for i in range(len(means)):
            nf_nxMx[i] -= abs(means[i] + ( (1 - (i / len(means)-1)) * stdevs[i]))

    nf_nxMx = np.clip(nf_nxMx, a_min=low, a_max=1.0)
    nf_nxMx2 = np.copy(nf_nxMx)

    spectrogram.data = nf_nxMx

    if outputPngName is not None:

        a = bf.LinearBand(low=int(spectrogram.metadata.min_freq),
                  high=int(spectrogram.metadata.max_freq),
                  nbands=20)

        energy = feat_energy.Energy()
        flux = feat_flux.Flux()
        rolloff = feat_rolloff.Rolloff()
        #centroid = feat_centroid.Centroid()
        lowen = []
        for b in a.bands():
            lowbin = spectrogram.freq_bin(b[0])
            highbin = spectrogram.freq_bin(b[1])
            en = inDb(energy.calc_track_band(spectrogram, lowbin, highbin).data)
            #print b[0], b[1], np.mean(en), np.std(en)
            #nf_nxMx[spectrogram.freq_bin(b[0])] = 1
            if np.mean(en) < -120:
                lowen.append((1, b, np.mean(en), np.std(en)))
            else:
                lowen.append((0, b, np.mean(en), np.std(en)))

        for i in lowen:
            print i
        print

        lowen = lowen[:11]
        #sorted(lowen, key = lambda b: b[2])
        lowen = sorted(lowen, key = lambda b: b[2], reverse=False)

        for i in lowen:
            print i

        bird = np.array([])
        birdlines = 0

        lowen = sorted(lowen[:1], key=lambda b: b[1][0])

        print

        for i in lowen:
            print "aaa", i

        max = lowen[0]
        min = lowen[0]

        for i in lowen:
            if i[1][1] > max[1][1]:
                max = i
            if i[1][0] < max[1][0]:
                min = i

        print "low", min[1][0], "high", max[1][1]

        for i in range(int(spectrogram.freq_bin(min[1][0])), int(spectrogram.freq_bin(max[1][1]))):
            bird = np.append(bird, nf_nxMx[i])
            birdlines+=1
            nf_nxMx2[i] = 1


        # for k in range(len(lowen)):
        #     #print k, lowen[k]
        #     #if lowen[k][0] == 1:
        #     if lowen[k][0] == lowen[k][0]:
        #         if lowen[k][1][0] < 10000:
        #             for i in range(int(spectrogram.freq_bin(lowen[k][1][0])), int(spectrogram.freq_bin(lowen[k][1][1]))):
        #                 bird = np.append(bird, nf_nxMx[i])
        #                 birdlines+=1
        #                 nf_nxMx2[i] = 1

        print

        output = np.copy(nf_nxMx)

        bird.shape = (birdlines, nf_nxMx.shape[1])

        for i in range(20):
            bird = np.vstack((np.ones(nf_nxMx.shape[1]), bird))

        output = np.vstack((output, bird))

        plt.imsave(outputPngName, inDb(output)[::-1])

    if plot:

        # plt.figure(0)
        # plt.plot(subs)
        # plt.figure(1)

        sbplt = plt.subplot(312)
        plt.pcolormesh(frmTime,
        binFreq,
        inDb(nf_nxMx))

        sbplt = plt.subplot(313)
        plt.pcolormesh(frmTime,
        binFreq,
        inDb(nf_nxMx2))

    if plot:
        plt.figure(1)
        plt.show(1)

    plt.close()


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
    filename = "./links/BAND_TAILED_NIGHTHAWK.3.wav"
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

    #remove_random_noise_from_wav(filename, True, 'foo.png', filter_compensation='log10', passes=1)
    remove_random_noise_from_wav(filename, True, 'foo2.png', filter_compensation='log10', passes=1)
    # remove_random_noise_from_wav(filename, True, None, filter_compensation='log10', passes=2)
    # remove_random_noise_from_wav(filename, True, None, filter_compensation='log10', passes=3)



