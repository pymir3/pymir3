import acf_utils
import sys
import numpy
import gc

sys.path.append("../../")

import mir3.data.feature_matrix as feature_matrix

class ModelTrainerInput:

    def __init__(self, features, labels):
        """
        :param features:
        :type features: numpy.array
        :param labels:
        :type labels: list[str]
        """
        self.features = features
        self.labels = labels

    # def __str__(self):
    #     return str(self.features) + str(self.features.shape) + str(self.labels)

class ModelTrainer:

    def __init__(self):
        pass

    @staticmethod
    def create(params):
        return acf_utils.behavior_factory(params, "model_training", "model_trainer","tr_")

    def run(self):

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

        input = ModelTrainerInput(features, labels)

        gc.collect()

        self.train(input)


    def train(self, train_data):
        raise NotImplementedError
        pass

