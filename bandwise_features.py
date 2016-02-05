import numpy as np
import scipy.io.wavfile
import copy
import mir3.lib.mir.features as mir
import mir3.lib.mir.mfcc as mfcc
import mir3.modules.features.filterbank as fbank
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
import mir3.modules.features.td_zero_crossings as feat_zerocrossings

import mir3.modules.features.join as feat_join
import mir3.modules.features.stats as feat_stats

class FrequencyBand:
    def bands(self):
        pass

class LinearBand(FrequencyBand):

    def __init__(self, low=0, high=22050, step=1000):
        self.low = low
        self.high = high
        self.step = step
        self.i = low


    def bands(self):
        for i in range(self.low, self.high, self.step):
            end = i + self.step
            if end > self.high:
                end = i + (self.step - (end - self.high))
            yield (i, end)


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

    def __init__(self, infile, dft_len=2048, window='hanning', window_len=2048, window_step=1024, db_spec = True):
        self.infile = infile
        self.dft_len = dft_len
        self.window_len = window_len
        self.window = window
        self.window_step = window_step
        self.db_spec = db_spec

        #load the auio file and compute its spectrum
        audio_file = open(infile, 'rb')
        self.spectrogram = wav2spec.Wav2Spectrogram().convert(audio_file, dft_length=dft_len,\
                                                              window_step=window_step,\
                                                              window_length=window_len)

        #keeping the time-domain data for computing time-domain features
        rate, audio_data = scipy.io.wavfile.read(infile)
        audio_data = audio_data.astype(np.float)
        audio_data /= np.max(np.abs(audio_data)) # Normalization to -1/+1 range
        self.audio_data = np.copy(audio_data)

        audio_file.close()

        if db_spec:
            self.spectrogram.data = 20 * np.log10(self.spectrogram.data + np.finfo(np.float).eps)

        self.band_features = np.array([])
        self.joined_features = None
        self.cropped = None

    def calculate_features_per_band(self, frequency_band):
        """
        :param frequency_band: FrequencyBand
        :return: list[FeatureTrack]
        """

        flatness = feat_flat.Flatness()
        energy = feat_energy.Energy()
        flux = feat_flux.Flux()
        centroid = feat_centroid.Centroid()
        rolloff = feat_rolloff.Rolloff()
        lowenergy = feat_lowenergy.LowEnergy()

        for b in frequency_band.bands():
            lowbin = self.spectrogram.freq_bin(b[0])
            highbin = self.spectrogram.freq_bin(b[1])
            #print "calculating features for band in bin range: ", lowbin, highbin

            features = []

            flatness_feature = flatness.calc_track_band(self.spectrogram, lowbin, highbin)
            flatness_feature.metadata.feature += ("_" + str(b[0]))
            features.append(flatness_feature)

            energy_feature = energy.calc_track_band(self.spectrogram, lowbin, highbin)
            energy_feature.metadata.feature += ("_" + str(b[0]))
            features.append(energy_feature)

            flux_feature = flux.calc_track_band(self.spectrogram, lowbin, highbin)
            flux_feature.metadata.feature += ("_" + str(b[0]))
            features.append(flux_feature)

            centroid_feature = centroid.calc_track_band(self.spectrogram, lowbin, highbin)
            centroid_feature.metadata.feature += ("_" + str(b[0]))
            features.append(centroid_feature)

            rolloff_feature = rolloff.calc_track_band(self.spectrogram, lowbin, highbin)
            rolloff_feature.metadata.feature += ("_" + str(b[0]))
            features.append(rolloff_feature)

            lowenergy_feature = lowenergy.calc_track_band(self.spectrogram, 10, lowbin, highbin)
            lowenergy_feature.metadata.feature += ("_" + str(b[0]))
            features.append(lowenergy_feature)

            #TODO: MFCCs e (caracteristicas no dominio do tempo? -- claro, sem separacao em bandas)

            self.band_features = np.hstack((self.band_features, features))

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
                    features[-1].data = np.resize(features[-1].data, min)

            self.joined_features = join.join(features)
            self.cropped = crop

        return self.joined_features

if __name__ == "__main__":
    #for i in a.bands():
    #    print i

    feats = BandwiseFeatures('/home/juliano/Music/genres_wav/rock.00000.wav')

    print feats.spectrogram.data.shape
    # plt.pcolormesh(feats.spectrogram.data)
    # plt.show()
    # plt.plot(feats.audio_data)
    # plt.show()
    a = LinearBand(low=int(feats.spectrogram.metadata.min_freq),
                   high=int(feats.spectrogram.metadata.max_freq),
                   step=1000)

    import time

    T0 = time.time()
    feats.calculate_features_per_band(a)
    T1 = time.time()
    print "Feature extraction took ", T1-T0, " seconds"

    print feats.join_bands(crop=True).data.shape

    stats = feat_stats.Stats()
    m = stats.stats([feats.joined_features], mean=True, variance=True, slope=False,limits=False, csv=False, normalize=False)

    print m.data

    #print feats.band_features[0]




