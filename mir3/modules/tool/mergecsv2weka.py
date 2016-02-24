import argparse
import csv
import numpy
import numpy.random

import mir3.data.feature_matrix as feature_matrix
import mir3.data.feature_track as track
import mir3.module

class MergeCSV2Weka(mir3.module.Module):
    def get_help(self):
        return """Merge feature matrix and CSV file with labels for using within
                    Weka"""

    def build_arguments(self, parser):
        parser.add_argument('database', type=argparse.FileType('rb'),
                            help="""input database""")
        parser.add_argument('labels', type=str,
                            help="""csv file with ground-truth labels""")

    def label_list(self, labelfile):
        file_label_dict = dict()
        lines = csv.reader(labelfile)
        for row in lines:
            file_label_dict[row[0]] = row[1]

        return file_label_dict

    #def open_ground_truth(self, csv):

    def run(self, args):
        a = feature_matrix.FeatureMatrix().load(args.database)
        file_label_dict = self.label_list(open(args.labels, 'rb'))

        # Start join process
        output = ""
        # Title row
        output += "filename,"
        for i in xrange(a.data.shape[1]):
            output += "F" + str(i) + ","
        output += "Class\n"

        for i in xrange(len(a.metadata.filename)):
            fname = a.metadata.filename[i].split('/')[-1]
            output += fname + ","
            for j in xrange(a.data.shape[1]):
                output += str(a.data[i][j]) + ","
            output += str(file_label_dict[fname]) + "\n"

        print output

