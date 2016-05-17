import sys
import logging
import time

sys.path.append("../../")
sys.path.append("../dcase2016/")

import bandwise_features as BF

from feature_extraction import FeatureExtractor

logger = logging.getLogger("feature_extraction")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

class BandwiseExtractor(FeatureExtractor):
    def __init__(self, params):
        pass

    def extract(self, filename):
        
        scale = self.params['bandwise_extraction']['scale']
        num_bands = self.params['bandwise_extraction']['number_of_bands']
        also_one_band = self.params['bandwise_extraction']['also_one_band']
        discard_bin_zero = self.params['bandwise_extraction']['discard_bin_zero']
        dft_len = self.params['general']['dft']['len']
        dft_window_size = self.params['general']['dft']['window_size']
        dft_window_step = self.params['general']['dft']['window_step']

        feats = BF.BandwiseFeatures(filename, dft_len=dft_len, window_len=dft_window_size, window_step=dft_window_step)

        if scale == 'one':
            a = BF.OneBand(low=int(feats.spectrogram.metadata.min_freq),
                           high=int(feats.spectrogram.metadata.max_freq))

        if scale == 'linear':
            a = BF.LinearBand(low=int(feats.spectrogram.metadata.min_freq),
                              high=int(feats.spectrogram.metadata.max_freq),
                              nbands=num_bands)
        if scale == 'mel':
            a = BF.MelBand(low=int(feats.spectrogram.metadata.min_freq),
                           high=int(feats.spectrogram.metadata.max_freq),
                           nbands=num_bands)

        logger.debug("Extracting features for %s", filename)
        T0 = time.time()
        feats.calculate_features_per_band(a, also_one_band=also_one_band, discard_bin_zero=discard_bin_zero)
        T1 = time.time()
        logger.debug("Feature extraction took %f seconds", T1 - T0)

        feats.join_bands(crop=True)
        return feats.joined_features