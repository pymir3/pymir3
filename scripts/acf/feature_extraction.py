# -*- coding: utf-8 -*-
import importlib
import gc
import time
from multiprocess import Pool
import acf_utils
import copy

class FeatureExtractor:
    """
    This is a base class used to extract audio features from a list of files.
    Its derived classes must implement the *extract* method.
    """

    def __init__(self):
        """
        FeatureExtractor is an abstract class. To use it you must extend it and then use the *create* static method
        as a factory.
        """
        pass

    @staticmethod
    def create(params):

        """
        This is a factory function that creates a feature extractor derived class
        from the parameter file. It dynamically loads the requested feature extractor class.

        :param params: A dictionary from a yaml experiment file.
        :type params: dict
        :return:
        :rtype: FeatureExtractor

        .. note::
            These keys are expected to be set in the experiment file:
                * ['feature_extraction']['extractor']

        """

        return acf_utils.behavior_factory(params, 'feature_extraction', 'extractor', "fe_")

    def extract(self, filename):
        """
        This is an abstract method that should implement feature extraction. This method must be implemented
        in the subclasses.

        :param filename: the full path to the file from which the features will be extracted.
        :type filename: str
        :return:
        :rtype: FeatureTrack
        """

        #One must implement this method in a subclass!
        raise NotImplementedError
        pass

    def run(self):
        """
        This functions reads the feature extraction filelist and creates a pool of processes to extract features
        from distinct files in parallel. It outputs one pymir3 FeatureTrack file per input file. Output is buffered
        to save memory and defer disk access.

        .. note::
            These keys are expected to be set in the experiment file:
                * ['general']['feature_extraction_filelist']
                * ['general']['scratch_directory']
                * ['feature_extraction']['output_buffer_size']
                * ['feature_extraction']['worker_extractors']

        """

        print("Running feature extraction behavior: %s" % self.name)

        # todo: use metadata file to add labels to track metadata (if available)
        # deve garantir a label no metadados pra facilitar a vida, ao invés de usar o nome do arquivo (acho que não precisa)

        with open(self.params['general']['feature_extraction_filelist']) as f:
            files = f.read().splitlines()

        # todo: usar um multiprocessing.manager pra realizar o compatilhamento do buffer (ao invés de fazer por chunks, como abaixo)

        metas = copy.copy(files)
        files = []
        for i in metas:
            files.append(i.split("\t")[0])
        metas = []

        num_files = len(files)
        output_buffer_size = self.params['feature_extraction']['output_buffer_size']

        pool = Pool(processes=self.params['feature_extraction']['worker_extractors'])
        for i in range(0, num_files, output_buffer_size):
            print "processing files %d through %d of %d" % (i + 1, min(i + output_buffer_size, num_files), num_files)
            result = pool.map(self.extract, files[i:min(i + output_buffer_size, num_files)])

            T0 = time.time()
            for track in result:
                filename = acf_utils.extract_filename(track.metadata.filename, "wav") + ".features"
                filename = self.params['general']['scratch_directory'] + "/" + filename

                print "writing features to file %s..." % (filename)
                feature_file = open(filename, "w")
                track.save(feature_file)
                feature_file.close()
                del track
            T1 = time.time()
            print "writing feature files to disk took %f seconds" % (T1 - T0)

            del result
            gc.collect()

        pool.close()
        pool.join()

        print ('Feature extraction done!')
