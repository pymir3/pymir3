import argparse
import numpy

import mir3.data.feature_matrix as feature_matrix
import mir3.data.feature_track as track
import mir3.lib.knn as knn
import mir3.module

class MinimumMutualDistance(mir3.module.Module):
    def get_help(self):
        return """Recommendations based on Minimum Mutual Distance"""

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

        # distmin algorithm
        score = numpy.array(knn.distance_mutual_min
                          (testing_data, training_data))

        for n in xrange(args.recommendations):
            k = score.argmin()
            print testing_files[k],
            score[k] =score.max()
        print ""
