import argparse
import numpy

import mir3.data.feature_matrix as feature_matrix
import mir3.data.feature_track as track
import mir3.lib.naive_bayes as bayes
import mir3.lib.pca as pca
import mir3.module

class PCABayes(mir3.module.Module):
    def get_help(self):
        return """Recommendations based on a naive bayes algorithm with a pca
        pre-processing step"""

    def build_arguments(self, parser):
        parser.add_argument('database', type=argparse.FileType('rb'),
                            help="""input database""")
        parser.add_argument('query', nargs='+', type=str,
                            help="""filenames used as inputs""")
        parser.add_argument('--recommendations', '-r',
                            type=int, default=5, help="""number of
                            files to recommend (default: %(default)s)""")

    def run(self, args):
        a = feature_matrix.FeatureMatrix().load(args.database)

        # Check if all inputs are valid and get their indexes
        missing_files = []
        file_indexes = []
        # print a.metadata.filename
        for fin in args.query:
            if fin not in a.metadata.filename:
                missing_files.append(fin)
            else:
                file_indexes.append(a.metadata.filename.index(fin))
        if len(missing_files) is not 0:
            print "Error: missing files!", missing_files
            exit()

        training_data = numpy.array([a.data[x,:] for x in file_indexes])
        testing_data = numpy.array([a.data[x,:] \
                            for x in range(len(a.metadata.filename)) \
                            if a.metadata.filename[x] not in args.query])
        testing_files = [a.metadata.filename[x] \
                         for x in range(len(a.metadata.filename)) \
                         if a.metadata.filename[x] not in args.query]

        # PCA algorithm
        orthogonal_testing, orthogonal_training = pca.subset_PCA \
                          (testing_data, training_data)

        # naive bayes algorithm
        score = numpy.array(bayes.naive_bayes
                          (orthogonal_testing, orthogonal_training))

        for n in xrange(args.recommendations):
            k = score.argmax()
            print testing_files[k],
            score[k] = 0.0
        print ""