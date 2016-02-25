import numpy as np
import logging
import glob
import bandwise_features as BF
import time
import mir3.modules.features.stats as feat_stats
import remove_random_noise as rrn

logger = logging.getLogger("birdclef_tza_bands")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def tza_bands():
    files = sorted(glob.glob("/home/juliano/Music/genres_wav/*.wav"))
    # files = sorted(glob.glob("links/*.wav"))
    numfiles = len(files)

    all_features = []
    k = 0
    for i in files:
        if k % 50 == 0:
            print float(k) / numfiles * 100, "% completed."
        k += 1

        feats = BF.BandwiseFeatures(i)

        # print feats.spectrogram.data.shape

        # a = BF.OneBand(low=int(feats.spectrogram.metadata.min_freq),
        #                high=int(feats.spectrogram.metadata.max_freq))

        # a = BF.LinearBand(low=int(feats.spectrogram.metadata.min_freq),
        #                   high=int(feats.spectrogram.metadata.max_freq),
        #                   step=1000)

        a = BF.MelBand(low=int(feats.spectrogram.metadata.min_freq),
                          high=int(feats.spectrogram.metadata.max_freq),
                          step=100)

        logger.debug("Extracting features for %s", i)
        T0 = time.time()
        feats.calculate_features_per_band(a)
        T1 = time.time()
        logger.debug("Feature extraction took %f seconds", T1 - T0)

        feats.join_bands(crop=True)
        all_features.append(feats.joined_features)

    stats = feat_stats.Stats()
    m = stats.stats(all_features, mean=True, variance=True, slope=False, limits=False, csv=False, normalize=True)

    f = open("genres_tza_mel_bands_100.fm", "wb")

    m.save(f)

    f.close()


def tza_bands_lessnoise():
    files = sorted(glob.glob("/home/juliano/Music/genres_wav/*.wav"))
    # files = sorted(glob.glob("links/*.wav"))
    numfiles = len(files)

    all_features = []
    k = 0
    for i in files:
        if k % 50 == 0:
            print float(k) / numfiles * 100, "% completed."
            100, "% completed."
        k += 1

        feats = BF.BandwiseFeatures(i, db_spec=False)

        rrn.remove_random_noise(feats.spectrogram, filter_compensation='log10', passes=1)
        feats.spec_to_db()

        # print feats.spectrogram.data.shape

        # a = BF.OneBand(low=int(feats.spectrogram.metadata.min_freq),
        #                high=int(feats.spectrogram.metadata.max_freq))

        # a = BF.LinearBand(low=int(feats.spectrogram.metadata.min_freq),
        #                   high=int(feats.spectrogram.metadata.max_freq),
        #                   step=1000)

        a = BF.MelBand(low=int(feats.spectrogram.metadata.min_freq),
                          high=int(feats.spectrogram.metadata.max_freq),
                          step=100)

        logger.debug("Extracting features for %s", i)
        T0 = time.time()
        feats.calculate_features_per_band(a)
        T1 = time.time()
        logger.debug("Feature extraction took %f seconds", T1 - T0)

        feats.join_bands(crop=True)
        all_features.append(feats.joined_features)

    stats = feat_stats.Stats()
    m = stats.stats(all_features, mean=True, variance=True, slope=False, limits=False, csv=False, normalize=True)

    f = open("genres_tza_mel_bands_100_lessnoise_log10.fm", "wb")

    m.save(f)

    f.close()


if __name__ == "__main__":
    #tza_bands()
    tza_bands_lessnoise()
