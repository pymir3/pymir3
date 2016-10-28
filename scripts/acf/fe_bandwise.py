import sys
import logging
import time
import traceback

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
    """
    This feature extractor calculates features for every frequency band interval from an interval set.
    The interval set, the number of intervals and other settings are found in the bandwise_extraction
    key in the experiment file.
    """

    def __init__(self):
        """
        Nothing special here.
        """
        pass

    def extract(self, filename):

        """
        This function extracts bandwise features from the file supplied.

        :param filename:
        :type filename:
        :return:
        :rtype: FeatureTrack

        .. note::
            These keys are expected to be set in the experiment file:
                * ['bandwise_extraction']['discard_bin_zero']
                * ['bandwise_extraction']['also_one_band']
                * ['bandwise_extraction']['number_of_bands']
                * ['bandwise_extraction']['scale']
                * ['general']['dft']['len']
                * ['general']['dft']['window_size']
                * ['general']['dft']['window_step']

        """

        try:
            
            scale = self.params['bandwise_extraction']['scale']
            num_bands = self.params['bandwise_extraction']['number_of_bands']
            also_one_band = self.params['bandwise_extraction']['also_one_band']
            discard_bin_zero = self.params['bandwise_extraction']['discard_bin_zero']
            dft_len = self.params['general']['dft']['len']
            dft_window_size = self.params['general']['dft']['window_size']
            dft_window_step = self.params['general']['dft']['window_step']
            desired_sample_rate = self.params['general']['sample_rate']
            to_mono = self.params['general']['mono']
            zero_pad_resampling = self.params['general']['zero_pad_resampling']

            T0 = time.time()
            logger.debug("Extracting features for %s", filename)

            #todo: handle file not found errors!

            feats = BF.BandwiseFeatures(filename,
                                        dft_len=dft_len,
                                        window_len=dft_window_size,
                                        window_step=dft_window_step,
                                        fs=desired_sample_rate,
                                        mono=to_mono,
                                        zero_pad_resampling=zero_pad_resampling)

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

            feats.calculate_features_per_band(a, also_one_band=also_one_band, discard_bin_zero=discard_bin_zero)
            T1 = time.time()
            logger.debug("Feature extraction took %f seconds", T1 - T0)

            feats.join_bands(crop=True)
            return feats.joined_features

        except Exception:
            traceback.print_exc()
            raise