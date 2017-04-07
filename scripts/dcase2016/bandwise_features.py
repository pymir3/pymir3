import sys
sys.path.append("../../")
import numpy as np
import scipy.io.wavfile
import copy
import gc
import mir3.modules.tool.wav2spectrogram as wav2spec
import mir3.data.spectrogram as spec
import mir3.data.feature_track as track
import matplotlib.pyplot as plt

import mir3.modules.features.flatness as feat_flat
import mir3.modules.features.energy as feat_energy
import mir3.modules.features.flux as feat_flux
import mir3.modules.features.centroid as feat_centroid
import mir3.modules.features.rolloff as feat_rolloff
import mir3.modules.features.low_energy as feat_lowenergy
import mir3.lib.mir.mfcc as mfcc
import mir3.lib.mir.tdom_features as tdomf

import mir3.modules.features.join as feat_join
import mir3.modules.features.stats as feat_stats
import mir3.modules.tool.threshold_spectrogram as threshold

class FrequencyBand:
    def bands(self):
        pass


class LinearBand(FrequencyBand):

    def __init__(self, low=0, high=22050, step=1000, nbands=None):
        self.low = low
        self.high = high
        self.step = step
        self.i = low
        self.nbands = nbands

    def bands(self):
        if self.nbands is not None:
            len = int(self.high / float(self.nbands))
            bands = []
            for i in range(self.nbands-1):
                bands.append((i*len, (i * len) + (len-1)))
            i+=1
            bands.append((i*len, self.high))
            for i in bands:
                yield i
        else:
            for i in range(self.low, self.high, self.step):
                end = i + self.step
                if end > self.high:
                    end = i + (self.step - (end - self.high))
                yield (i, end)


class OneBand(FrequencyBand):

    def __init__(self, low=0, high=22050):
        self.low = low
        self.high = high

    def bands(self):
        yield (self.low, self.high)


def mel_to_hz(mel):
    return 700 * (10**(float(mel) / 2595)-1)


def hz_to_mel(hz):
    return 2595 * np.log10(1 + (float(hz) / 700))


class MelBand(FrequencyBand):

    def __init__(self, low=0, high=22050, step = 300, nbands=None):
        self.low = low
        self.high = high
        self.step = step
        self.low_mel = hz_to_mel(low)
        self.high_mel = hz_to_mel(high)
        self.nbands = nbands

        #print "low hz = %d, low mel = %d, high hz = %d, high mel = %d" % (self.low, self.low_mel, self.high, self.high_mel)


    def bands(self):

        if self.nbands is not None:
            len = int(self.high_mel / float(self.nbands))
            bands = []
            for i in range(self.nbands-1):
                bands.append((i*len, (i * len) + (len-1)))
            i+=1
            bands.append((i*len, self.high_mel))
            for i in bands:
                yield (int(np.floor(mel_to_hz(i[0]))), int(np.floor(mel_to_hz(i[1]))))
        else:
            for i in range(np.int(self.low_mel), np.int(self.high_mel), self.step):
                beg = int(np.floor(mel_to_hz(i)))
                end = int(np.floor(mel_to_hz(i + self.step)))-1
                if end > self.high:
                    end = self.high
                yield (beg, end)



class BandwiseFeatures:
    """
    :type infile: string
    :type dft_len: int
    :type window: string
    :type window_len: int
    :type window_step: int
    :type db_spec: boolean
    :type band_features: np.ndarray
    :type spectrogram mir3.data.Spectrogram
    """

    def __init__(self, infile, dft_len=2048, window='hanning', window_len=2048, window_step=1024, db_spec = True,
                                            fs = 44100, mono = True, zero_pad_resampling=False, threshold_cut=None ):
        self.infile = infile
        self.dft_len = dft_len
        self.window_len = window_len
        self.window = window
        self.window_step = window_step
        self.db_spec = db_spec
        self.features_per_band = 0
        self.threshold_cut = threshold_cut

        #load the auio file and compute its spectrum
        #audio_file = open(infile, 'rb')

        rate, audio_data = wav2spec.Wav2Spectrogram().load_audio(infile, fs=fs, mono=mono,
                                                                 zero_pad_resampling=zero_pad_resampling)
        audio_data = audio_data.astype(np.float)
        audio_file = open(infile, 'rb')

        # mean 0, var 1
        audio_data -= np.mean(audio_data)
        audio_data /= np.var(audio_data) ** (0.5)

        # audio_data /= np.max(np.abs(audio_data)) # Normalization to -1/+1 range

        self.spectrogram = wav2spec.Wav2Spectrogram().convert(audio_file, dft_length=dft_len,\
                                                              window_step=window_step,\
                                                              window_length=window_len,
                                                              wav_rate=rate,
                                                              wav_data=audio_data)

        if self.threshold_cut is not None:
            self.spectrogram = threshold.ThresholdSpectrogram().threshold(self.spectrogram, self.threshold_cut, overwrite_spec=True)

        # keeping the time-domain data for computing time-domain features
        self.audio_data = audio_data
        self.samplingrate = rate

        if db_spec:
            self.spectrogram.data = 20 * np.log10(self.spectrogram.data + np.finfo(np.float).eps)

        self.band_features = np.array([])
        self.joined_features = None
        self.cropped = None

    def spec_to_db(self):
        self.spectrogram.data = 20 * np.log10(self.spectrogram.data + np.finfo(np.float).eps)

    def calculate_features_per_band(self, frequency_band, also_one_band=False, discard_bin_zero=False):
        """
        :param frequency_band: FrequencyBand
        :param also_one_band: boolean
        :param discard_bin_zero: boolean
        :return: list[FeatureTrack]
        """

        flatness = feat_flat.Flatness()
        energy = feat_energy.Energy()
        flux = feat_flux.Flux()
        centroid = feat_centroid.Centroid()
        rolloff = feat_rolloff.Rolloff()
        lowenergy = feat_lowenergy.LowEnergy()

        bands = [b for b in frequency_band.bands()]

        if also_one_band:
            bands.append((int(frequency_band.low), int(frequency_band.high)))

        for b in bands:
            lowbin = self.spectrogram.freq_bin(b[0])
            if lowbin == 0:
                if discard_bin_zero:
                    lowbin = 1
            highbin = self.spectrogram.freq_bin(b[1])
            #print "calculating features for band in bin range: ", lowbin, highbin

            features = []

            flatness_feature = flatness.calc_track_band(self.spectrogram, lowbin, highbin)
            flatness_feature.metadata.feature += ("_" + str(b[0])) + ("_" + str(b[1]))
            features.append(flatness_feature)

            energy_feature = energy.calc_track_band(self.spectrogram, lowbin, highbin)
            energy_feature.metadata.feature += ("_" + str(b[0])) + ("_" + str(b[1]))
            features.append(energy_feature)

            flux_feature = flux.calc_track_band(self.spectrogram, lowbin, highbin)
            flux_feature.metadata.feature += ("_" + str(b[0])) + ("_" + str(b[1]))
            features.append(flux_feature)

            centroid_feature = centroid.calc_track_band(self.spectrogram, lowbin, highbin)
            centroid_feature.metadata.feature += ("_" + str(b[0])) + ("_" + str(b[1]))
            features.append(centroid_feature)

            rolloff_feature = rolloff.calc_track_band(self.spectrogram, lowbin, highbin)
            rolloff_feature.metadata.feature += ("_" + str(b[0])) + ("_" + str(b[1]))
            features.append(rolloff_feature)

            lowenergy_feature = lowenergy.calc_track_band(self.spectrogram, 10, lowbin, highbin)
            lowenergy_feature.metadata.feature += ("_" + str(b[0])) + ("_" + str(b[1]))
            features.append(lowenergy_feature)

            self.features_per_band = len(features)

            self.band_features = np.hstack((self.band_features, features))

        #MFCC hack
        t = track.FeatureTrack()
        t.data = mfcc.mfcc(self.spectrogram,20)
        t.metadata.sampling_configuration = self.spectrogram.metadata.sampling_configuration
        feature = ""
        for i in range(20):
            feature = feature + "MFCC_"+ str(i) + " "
        feature = feature.strip()
        t.metadata.feature = feature
        t.metadata.filename = self.spectrogram.metadata.input.name

        self.band_features = np.hstack((self.band_features, t))

        #Zero crossings
        t = track.FeatureTrack()
        t.data = tdomf.zero_crossings(self.audio_data, 1024, 512)
        t.metadata.sampling_configuration.fs = self.samplingrate
        t.metadata.sampling_configuration.ofs = self.samplingrate / 1024
        t.metadata.sampling_configuration.window_length = 512
        t.metadata.feature = "TDZeroCrossings"
        t.metadata.filename = self.spectrogram.metadata.input.name

        self.band_features = np.hstack((self.band_features, t))

        gc.collect()

    def join_bands(self, crop=False):

        if self.cropped is not None:
            if self.cropped != crop:
                self.joined_features = None

        if self.joined_features is None:

            join = feat_join.Join()

            features = self.band_features

            if crop:
                min = np.min( [x.data.shape for x in self.band_features] )
                features = []
                for i in self.band_features:
                    features.append(copy.copy(i))
                    if features[-1].data.ndim > 1:
                        features[-1].data = np.resize(features[-1].data, (min[0], features[-1].data.shape[1]))
                    else:
                        features[-1].data = np.resize(features[-1].data, min)

                    if features[-1].data.ndim > 2:
                        print "ERROR: unexpected number of dimensions."

            self.joined_features = join.join(features)
            self.cropped = crop

        return self.joined_features

if __name__ == "__main__":
    #for i in a.bands():
    #    print i

    #feats = BandwiseFeatures('/home/juliano/base_teste_rafael_94_especies/BUFF_NECKED_IBIS/LIFECLEF2015_BIRDAMAZON_XC_WAV_RN26407.wav')
    feats = BandwiseFeatures('/home/juliano/Music/genres_wav/rock.00000.wav', dft_len=2048, window_len=1763, window_step=882, db_spec=True)
    #feats2 = BandwiseFeatures('/home/juliano/Music/genres_wav/rock.00000.wav', dft_len=2048, window_len=1024, window_step=256, db_spec=True)

    print feats.spectrogram.data.shape
    plt.figure(0)
    # plt.pcolormesh(feats.spectrogram.data)
    # plt.figure(1)
    # plt.pcolormesh(feats2.spectrogram.data)
    # plt.show()
    # exit(0)
    # plt.plot(feats.audio_data)
    # plt.show()
    a = LinearBand(low=int(feats.spectrogram.metadata.min_freq),
                   high=int(feats.spectrogram.metadata.max_freq),
                   nbands=10)

    b = MelBand(low=int(feats.spectrogram.metadata.min_freq),
                   high=int(feats.spectrogram.metadata.max_freq),
                   nbands=20)
    import time

    # b = OneBand(low=int(feats.spectrogram.metadata.min_freq),
    #                high=int(feats.spectrogram.metadata.max_freq))

    for k in a.bands():
        print k


    T0 = time.time()
    feats.calculate_features_per_band(b, True)
    T1 = time.time()
    print "Feature extraction took ", T1-T0, " seconds"

    print feats.join_bands(crop=True).data.shape

    print "lalalallal", feats.joined_features.metadata.feature

    stats = feat_stats.Stats()
    m = stats.stats([feats.joined_features], mean=True, variance=True, delta=True, slope=False,limits=False, csv=False, normalize=False)

    print m.data.shape
    print m.data

    #print feats.band_features[0]




