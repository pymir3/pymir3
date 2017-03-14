# -*- coding: utf-8 -*-
import gc
import os
import acf_utils
import sys
import numpy

sys.path.append("../../")

import mir3.data.feature_matrix as feature_matrix
import mir3.data.feature_track as feature_track

class ModelTesterInput:
    def __init__(self, features, filenames, itype):
        self.features = features
        self.filenames = filenames
        self.type = itype

class ModelTester:

    def __init__(self):
        pass

    @staticmethod
    def create(params):
        return acf_utils.behavior_factory(params, 'model_testing', 'model_tester', 'tst_')

    def run(self):

        if self.params['model_testing']['test_input_type'] == 'feature_matrix':

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

            input = ModelTesterInput(features, test_filenames, 'matrix')

            gc.collect()

            self.test(input)

        else:

            if self.params['model_testing']['test_input_type'] == 'feature_tracks':

                with open(self.params['general']['test_filelist']) as f:
                    ffiles = f.readlines()

                filenames = []
                labels_f = []

                for l in ffiles:
                    d = l.split('\t')
                    if len(d) < 2:
                        break
                    filenames.append(d[0].strip())
                    labels_f.append(d[1].strip())
                
                filenames_features = map(lambda x: self.params['general']['scratch_directory'] + "/" + os.path.basename(x) + '.features', filenames)

                features = []
                labels = []

                for f in xrange(len(filenames_features)):
                    track = feature_track.FeatureTrack()
                    trackfile = open(filenames_features[f], mode='r')
                    track = track.load(trackfile)
                    trackfile.close()
                    
                    ft = track.data

                    if not numpy.any(numpy.isnan(ft)):
                        features.append(ft)
                        labels.append(labels_f[f])
                
                filenames_features = None
                ft = None

                features = numpy.array(features)

                input = ModelTesterInput(features, filenames, 'tracks')
                    
                gc.collect()

                self.test(input)                

    def test(self, test_data):
        raise NotImplementedError
