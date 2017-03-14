import acf_utils
import sys
import numpy
import gc
import os

sys.path.append("../../")

import mir3.data.feature_matrix as feature_matrix
import mir3.data.feature_track as feature_track
import mir3.modules.features.join as join

class ModelTrainerInput:

    def __init__(self, features, labels, itype):
        """
        :param features:
        :type features: numpy.array
        :param labels:
        :type labels: list[str]
        """
        self.features = features
        self.labels = labels
        self.type = itype

class ModelTrainer:

    def __init__(self):
        pass

    @staticmethod
    def create(params):
        return acf_utils.behavior_factory(params, "model_training", "model_trainer","tr_")

    def run(self):

        print "training model from train filelist: %s" % (self.params['general']['train_filelist'])

        if self.params['model_training']['train_input_type'] == 'feature_matrix':

            m = feature_matrix.FeatureMatrix()
            mf = open(self.params['general']['scratch_directory'] + "/" + self.params['feature_aggregation']['aggregated_output'])
            m = m.load(mf)
            mf.close()

            with open(self.params['general']['train_filelist']) as f:
                linhas = f.readlines()

            files = dict()

            for i in xrange(len(m.metadata.filename)):
                files[m.metadata.filename[i]] = i

            labels = []
            features = []

            for i in xrange(len(linhas)):
                filename = linhas[i].split("\t")[0].strip()
                label = linhas[i].split("\t")[1].strip()
                labels.append(label)

                feat = m.data[files[filename]]
                features.append(feat)

            features = numpy.array(features)

            files = None

            input = ModelTrainerInput(features, labels, 'matrix')

            gc.collect()

            self.train(input)

        else:
            if self.params['model_training']['train_input_type'] == 'feature_tracks':

                with open(self.params['general']['train_filelist']) as f:
                    ffiles = f.readlines()

                filenames = []
                labels_f = []

                for l in ffiles:
                    d = l.split('\t')
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

                input = ModelTrainerInput(features, labels, 'tracks')
                    
                gc.collect()

                self.train(input)

    def train(self, train_data):
        raise NotImplementedError
        pass

