import argparse
import copy
import numpy
import scipy.stats
import sys

import mir3.data.self_similarity_matrix as self_similarity_matrix
import mir3.data.feature_track as track
import mir3.lib.self_similarity as self_similarity
import mir3.module

class SelfSimilarity(mir3.module.Module):
    def get_help(self):
        return """Outputs a self-similarity matrix related to the input feature track."""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""input track file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""output file""")
        parser.add_argument('-n','--normalize', action='store_true',
                            default=True, help="""normalize each input column
                            to 0 mean and unit variance (default:
                            %(default)s)""")

    def run(self, args):
        o = track.FeatureTrack()

        final_output = None
        final_filenames = []

        o = o.load(args.infile)

        p = self_similarity_matrix.SelfSimilarityMatrix()

        data = o.data
        
        if args.normalize:
            std_p = data.std(axis=0)
            data = (data - data.mean(axis=0))/\
                    numpy.maximum(10**(-6), std_p)

        p.data = self_similarity.self_similarity_euclidean(data)

        p.metadata.feature = o.metadata.feature
        p.metadata.sampling_configuration = o.metadata.sampling_configuration
        p.metadata.filename = o.metadata.filename

        p.save(args.outfile)
