import argparse
import csv
import numpy
import copy

import mir3.data.feature_matrix as feature_matrix
import mir3.data.feature_track as track
import mir3.module

class ThresholdSpectrogram(mir3.module.Module):
    def get_help(self):
        return """Sets spectrogram components smaller than a threshold in dB to 0 in linear scale"""

    def build_arguments(self, parser):
        parser.add_argument('spectrectrogram_file', type=argparse.FileType('rb'),
                            help="""input spectrogram""")
        parser.add_argument('output_spectrogram', type=argparse.FileType('rb'),
                            help="""output spectrogram""")

    def threshold(self, input_spec, threshold=-70, overwrite_spec=False):

        if overwrite_spec:
            out = input_spec
        else
            out = copy.deepcopy(input_spec)

        data = out.data
        M = np.max(data)
        F = data / M
        k = 20 * np.log10(F)
        k[k >= threshold] = 1
        k[k <  threshold] = 0
        data = data * k
        out.data = data

        return out

    def run(self, args):
        raise NotImplementedError

