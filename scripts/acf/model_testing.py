# -*- coding: utf-8 -*-
import gc

import acf_utils
import sys
import numpy

sys.path.append("../../")

import mir3.data.feature_matrix as feature_matrix

class ModelTesterInput:
    def __init__(self, features, filenames):
        self.features = features
        self.filenames = filenames


class ModelTester:

    def __init__(self):
        pass

    @staticmethod
    def create(params):
        return acf_utils.behavior_factory(params, 'model_testing', 'model_tester', 'tst_')

    def run(self):

        print "testing model from train filelist: %s" % (self.params['general']['test_filelist'])

        m = feature_matrix.FeatureMatrix()
        mf = open(self.params['general']['scratch_directory'] + "/" + self.params['feature_aggregation']['aggregated_output'])
        m = m.load(mf)
        mf.close()

        with open(self.params['general']['test_filelist']) as f:
            linhas = f.readlines()

        files = dict()

        for i in xrange(len(m.metadata.filename)):
            files[m.metadata.filename[i]] = i

        features = []
        test_filenames = []

        for i in xrange(len(linhas)):
            filename = linhas[i].split("\t")[0].strip()
            test_filenames.append(filename)

            feat = m.data[files[filename]]
            features.append(feat)

        features = numpy.array(features)

        files = None

        input = ModelTesterInput(features, test_filenames)

        gc.collect()

        self.test(input)

    def test(self, test_data):
        raise NotImplementedError