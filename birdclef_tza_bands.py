import numpy as np
import logging
import glob
import bandwise_features as BF
import time
import mir3.modules.features.stats as feat_stats
import remove_random_noise as rrn
from multiprocessing import Pool

logger = logging.getLogger("birdclef_tza_bands")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class BandJob:
    """
    :type filename: string
    :type band_iterator: string
    :type band_step: int
    :type lnf_use: bool
    :type lnf_compensation: string
    :type lnf_passes: int
    """

    def __init__(self, filename, band_iterator='mel', band_step=500, lnf_use=False, lnf_compensation='log10', lnf_passes=1):
        self.filename = filename
        self.band_iterator = band_iterator
        self.band_step = band_step
        self.lnf_use = lnf_use
        self.lnf_compensation = lnf_compensation
        self.lnf_passes = lnf_passes


class BandExperiment:

    def __init__(self, wav_path, output_file,
                 band_iterator='mel',
                 band_step=500,
                 lnf_use=False,
                 lnf_compensation='log10',
                 lnf_passes=1,
                 mean=True, variance=True, slope=False, limits=False, csv=False, normalize=True):
        self.wav_path=wav_path
        self.output_file=output_file
        self.band_iterator=band_iterator
        self.band_step=band_step
        self.lnf_use=lnf_use
        self.lnf_compensation=lnf_compensation
        self.lnf_passes=lnf_passes
        self.mean=mean
        self.variance=variance
        self.slope=slope
        self.limits=limits
        self.csv=csv
        self.normalize=normalize


def tza_bands_parallel(experiment, n_processes = 1):
    """
    :type experiment: BandExperiment
    :type n_processes: int
    """

    files = sorted(glob.glob(experiment.wav_path + "*.wav"))
    jobs = []
    for f in files:
        jobs.append(BandJob(f, experiment.band_iterator, experiment.band_step,
                            lnf_use=experiment.lnf_use,
                            lnf_compensation=experiment.lnf_compensation,
                            lnf_passes=experiment.lnf_passes))

    pool = Pool(processes=n_processes)

    features = pool.map(tza_bands, jobs)

    stats = feat_stats.Stats()
    m = stats.stats(features,
                    mean=experiment.mean,
                    variance=experiment.variance,
                    slope=experiment.slope,
                    limits=experiment.limits,
                    csv=experiment.csv,
                    normalize=experiment.normalize)

    f = open(experiment.output_file, "wb")

    m.save(f)

    f.close()


def tza_bands(job):
    """
    :type job: BandJob
    """

    if job.lnf_use:
        feats = BF.BandwiseFeatures(job.filename, db_spec=False)
        rrn.remove_random_noise(feats.spectrogram, filter_compensation=job.lnf_compensation, passes=job.lnf_passes)
        feats.spec_to_db()
    else:
        feats = BF.BandwiseFeatures(job.filename)

    if job.band_iterator == 'one':
        a = BF.OneBand(low=int(feats.spectrogram.metadata.min_freq),
                       high=int(feats.spectrogram.metadata.max_freq))

    if job.band_iterator == 'linear':
        a = BF.LinearBand(low=int(feats.spectrogram.metadata.min_freq),
                          high=int(feats.spectrogram.metadata.max_freq),
                          step=job.band_step)
    if job.band_iterator == 'mel':
        a = BF.MelBand(low=int(feats.spectrogram.metadata.min_freq),
                          high=int(feats.spectrogram.metadata.max_freq),
                          step=job.band_step)

    logger.debug("Extracting features for %s", job.filename)
    T0 = time.time()
    feats.calculate_features_per_band(a)
    T1 = time.time()
    logger.debug("Feature extraction took %f seconds", T1 - T0)

    feats.join_bands(crop=True)
    return feats.joined_features

if __name__ == "__main__":
    exp = BandExperiment("./links/", "birdclef_tza_mel_bands_1000.fm", band_iterator='mel', band_step=500)
    tza_bands_parallel(exp, n_processes=4)
