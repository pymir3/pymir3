import argparse

import mir3.data.spectrogram as spectrogram
import mir3.module

class Spectrogram(mir3.module.Module):
    def get_help(self):
        return """outputs a matrix in ASCII for the spectrogram"""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('rb'))

    def run(self, args):
        s = spectrogram.Spectrogram().load(args.infile)
        for i in range(s.data.shape[0]):
            for j in range(s.data.shape[1]):
                print '%e' % s.data[i,j],
            print ''
