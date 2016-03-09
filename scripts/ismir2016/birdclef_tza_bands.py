import numpy as np
import logging
import glob
import bandwise_features as BF
import time
import mir3.modules.features.stats as feat_stats
import mir3.modules.tool.to_texture_window as texture_window
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

    def __init__(self, filename, band_iterator='mel', band_step=500, band_nbands=None, lnf_use=False, lnf_compensation='log10', lnf_passes=1):
        self.filename = filename
        self.band_iterator = band_iterator
        self.band_step = band_step
        self.band_nbands = band_nbands
        self.lnf_use = lnf_use
        self.lnf_compensation = lnf_compensation
        self.lnf_passes = lnf_passes


class BandExperiment:

    def __init__(self, mirex_list_file, mirex_scratch_folder,
                 output_file,
                 band_iterator='mel',
                 band_step=500,
                 band_nbands=None,
                 lnf_use=False,
                 lnf_compensation='log10',
                 lnf_passes=1,
                 mean=True, variance=True, slope=False, limits=False, csv=False, normalize=True):

        self.mirex_list_file=mirex_list_file
        self.mirex_scratch_folder=mirex_scratch_folder
        self.output_file=output_file
        self.band_iterator=band_iterator
        self.band_step=band_step
        self.band_nbands=band_nbands
        self.lnf_use=lnf_use
        self.lnf_compensation=lnf_compensation
        self.lnf_passes=lnf_passes
        self.mean=mean
        self.variance=variance
        self.slope=slope
        self.limits=limits
        self.csv=csv
        self.normalize=normalize

# def tza_sep_bands_parallel(experiment, n_processes = 1):
#     """
#     :type experiment: BandExperiment
#     :type n_processes: int
#     """
#
#     files = sorted(glob.glob(experiment.wav_path + "*.wav"))
#     jobs = []
#     for f in files:
#         jobs.append(BandJob(f, experiment.band_iterator, experiment.band_step, experiment.band_nbands,
#                             lnf_use=experiment.lnf_use,
#                             lnf_compensation=experiment.lnf_compensation,
#                             lnf_passes=experiment.lnf_passes))
#
#     pool = Pool(processes=n_processes)
#
#     features = pool.map(tza_sep_bands, jobs)
#
#     pool.close()
#     pool.join()
#
#     n_bands = (len(features[0]) - 2) / 6
#
#     print "number of bands: ", n_bands, len(features[0])
#
#     bands = dict()
#
#     for band in features:
#         for i in range(0, len(band)-2, 6):
#             track_feats = []
#             for k in range(6):
#                 track_feats.append(band[i+k])
#             key = band[i].metadata.feature.split("_")[1]
#             if not bands.has_key(key):
#                 bands[key] = []
#             bands[key].append(track_feats)
#
#     for band in bands:
#         print band
#         for track in bands[band]:
#             print track[0].metadata.filename
#             for feature in track:
#                 print feature.metadata.feature
#
#     #TODO: tenho que fazer o feats.join....  pra fazer o join precisa de um objeto Bandwise features
#     #for band in bands:
#
#
#     #
#     # stats = feat_stats.Stats()
#     # m = stats.stats(features,
#     #                 mean=experiment.mean,
#     #                 variance=experiment.variance,
#     #                 slope=experiment.slope,
#     #                 limits=experiment.limits,
#     #                 csv=experiment.csv,
#     #                 normalize=experiment.normalize)
#     #
#     # f = open(experiment.output_file, "wb")
#     #
#     # m.save(f)
#     #
#     # f.close()
#
# def tza_sep_bands(job):
#     """
#     :type job: BandJob
#     """
#
#     if job.lnf_use:
#         feats = BF.BandwiseFeatures(job.filename, db_spec=False)
#         rrn.remove_random_noise(feats.spectrogram, filter_compensation=job.lnf_compensation, passes=job.lnf_passes)
#         feats.spec_to_db()
#     else:
#         feats = BF.BandwiseFeatures(job.filename)
#
#     if job.band_iterator == 'one':
#         a = BF.OneBand(low=int(feats.spectrogram.metadata.min_freq),
#                        high=int(feats.spectrogram.metadata.max_freq))
#
#     if job.band_iterator == 'linear':
#         a = BF.LinearBand(low=int(feats.spectrogram.metadata.min_freq),
#                           high=int(feats.spectrogram.metadata.max_freq),
#                           step=job.band_step,
#                           nbands=job.band_nbands)
#     if job.band_iterator == 'mel':
#         a = BF.MelBand(low=int(feats.spectrogram.metadata.min_freq),
#                           high=int(feats.spectrogram.metadata.max_freq),
#                           step=job.band_step,
#                           nbands=job.band_nbands)
#
#     logger.debug("Extracting features for %s", job.filename)
#     T0 = time.time()
#     feats.calculate_features_per_band(a)
#     T1 = time.time()
#     logger.debug("Feature extraction took %f seconds", T1 - T0)
#
#     return feats.band_features


def tza_bands_parallel(experiment, n_processes = 1):
    """
    :type experiment: BandExperiment
    :type n_processes: int
    """

    with open(experiment.mirex_list_file) as f:
        files = f.read().splitlines()

    jobs = []
    for f in files:
        jobs.append(BandJob(f, experiment.band_iterator, experiment.band_step, experiment.band_nbands,
                            lnf_use=experiment.lnf_use,
                            lnf_compensation=experiment.lnf_compensation,
                            lnf_passes=experiment.lnf_passes))

    #calculate features
    pool = Pool(processes=n_processes)
    features = pool.map(tza_bands, jobs)
    pool.close()
    pool.join()

    jobs = []
    for f in features:
        jobs.append((f, 100))

    #calculate texture windows
    pool = Pool(processes=n_processes)
    textures = pool.map(tza_calc_textures, jobs)
    pool.close()
    pool.join()

    stats = feat_stats.Stats()
    m = stats.stats(textures,
                    mean=experiment.mean,
                    variance=experiment.variance,
                    slope=experiment.slope,
                    limits=experiment.limits,
                    csv=experiment.csv,
                    normalize=experiment.normalize)

    f = open(experiment.mirex_scratch_folder + "/" + experiment.output_file, "wb")

    m.save(f, restore_state=True)

    f.close()

    return m

def tza_calc_textures(args):
    tw = texture_window.ToTextureWindow()
    feature = args[0]
    logger.debug("calculating textures for %s", feature.metadata.filename)
    return tw.to_texture(feature, args[1])

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
                          step=job.band_step,
                          nbands=job.band_nbands)
    if job.band_iterator == 'mel':
        a = BF.MelBand(low=int(feats.spectrogram.metadata.min_freq),
                          high=int(feats.spectrogram.metadata.max_freq),
                          step=job.band_step,
                          nbands=job.band_nbands)

    logger.debug("Extracting features for %s", job.filename)
    T0 = time.time()
    feats.calculate_features_per_band(a)
    T1 = time.time()
    logger.debug("Feature extraction took %f seconds", T1 - T0)

    feats.join_bands(crop=True)
    return feats.joined_features


def MIREX_ExtractFeatures(scratch_folder, feature_extraction_list, **kwargs):
    exp = BandExperiment(feature_extraction_list, scratch_folder,
                         output_file=kwargs['output_file'],
                         band_iterator=kwargs['band_iterator'],
                         band_nbands=kwargs['band_nbands'])
    return tza_bands_parallel(exp, n_processes=4)

if __name__ == "__main__":
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_linear_bands_500.fm", band_iterator='linear', band_step=500)
    # tza_bands_parallel(exp, n_processes=4)
    #
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_linear_bands_1000.fm", band_iterator='linear', band_step=1000)
    # tza_bands_parallel(exp, n_processes=4)
    #
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_linear_bands_2000.fm", band_iterator='linear', band_step=2000)
    # tza_bands_parallel(exp, n_processes=4)
    #
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_mel_bands_100.fm", band_iterator='mel', band_step=100)
    # tza_bands_parallel(exp, n_processes=4)
    #
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_mel_bands_300.fm", band_iterator='mel', band_step=300)
    # tza_bands_parallel(exp, n_processes=4)
    #
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_mel_bands_500.fm", band_iterator='mel', band_step=500)
    # tza_bands_parallel(exp, n_processes=4)
    #
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_mel_bands_1000.fm", band_iterator='mel', band_step=1000)
    # tza_bands_parallel(exp, n_processes=4)
    #
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_one_band.fm", band_iterator='one')
    # tza_bands_parallel(exp, n_processes=4)

    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_linear_10b.fm", band_iterator='linear', band_nbands=10)
    # tza_bands_parallel(exp, n_processes=4)

    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_linear_30b.fm", band_iterator='linear', band_nbands=30)
    # tza_bands_parallel(exp, n_processes=4)
    #
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_linear_50b.fm", band_iterator='linear', band_nbands=50)
    # tza_bands_parallel(exp, n_processes=4)
    #
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_mel_10b.fm", band_iterator='mel', band_nbands=10)
    # tza_bands_parallel(exp, n_processes=4)
    #
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_mel_30b.fm", band_iterator='mel', band_nbands=30)
    # tza_bands_parallel(exp, n_processes=4)
    #
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_mel_50b.fm", band_iterator='mel', band_nbands=50)
    # tza_bands_parallel(exp, n_processes=4)

    ####WITHTEXTURES############

    MIREX_ExtractFeatures("fm/genres", "genres_file_list.txt", output_file="teste.fm", band_iterator='mel', band_nbands=10)

    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_one_band_tex.fm", band_iterator='one')
    # tza_bands_parallel(exp, n_processes=4)

    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_linear_10b_tex.fm", band_iterator='linear', band_nbands=10)
    # tza_bands_parallel(exp, n_processes=4)
    #
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_linear_30b_tex.fm", band_iterator='linear', band_nbands=30)
    # tza_bands_parallel(exp, n_processes=4)
    #
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_linear_50b_tex.fm", band_iterator='linear', band_nbands=50)
    # tza_bands_parallel(exp, n_processes=4)
    #
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_mel_10b_tex.fm", band_iterator='mel', band_nbands=10)
    # tza_bands_parallel(exp, n_processes=4)
    #
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_mel_30b_tex.fm", band_iterator='mel', band_nbands=30)
    # tza_bands_parallel(exp, n_processes=4)
    #
    # exp = BandExperiment("/home/juliano/Music/genres_wav/", "fm/genres/genres_tza_mel_50b_tex.fm", band_iterator='mel', band_nbands=50)
    # tza_bands_parallel(exp, n_processes=4)

    #exp = BandExperiment("./lesslinks/", "sepbands", band_iterator='mel', band_nbands=10)
    #tza_sep_bands_parallel(exp, n_processes=4)