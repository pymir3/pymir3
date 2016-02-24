# Plots a spectrogram as a figure. This should be a good app to 

import argparse
import matplotlib.pyplot as plt
import numpy
import mir3.data.self_similarity_matrix as ssm

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help="""spectrogram file""")
    parser.add_argument('outfile', help="""target image file""")

    parser.add_argument('-t','--minimum_time', 
        default=0, help="""Minimum time (s) to plot""")
    parser.add_argument('-T','--maximum_time', 
        default=None, help="""Maximum time (s) to plot""")
    parser.add_argument('-W', '--width',
        default=400, help="""Plot width (px)""")
    parser.add_argument('-H', '--height',
        default=400, help="""Plot height (px)""")

    args = parser.parse_args()

    s = ssm.SelfSimilarityMatrix()
    s = s.load(open(args.infile))

    maxT = s.data.shape[1]
    maxTs = maxT / s.metadata.sampling_configuration.ofs

    out = s.data
    out = out/numpy.max(out)
    out = 1 - out

    im=plt.imshow(out, aspect='auto', origin='lower', cmap=plt.cm.gray,
        extent=[0, maxTs, 0, maxTs])
    plt.xlabel('Time (s)')
    plt.ylabel('Time (s)')
    fig = plt.gcf()

    size = (args.width, args.height)
    width_inches = size[0]/80.0
    height_inches = size[1]/80.0
    fig.set_size_inches((width_inches,height_inches))

    plt.savefig(args.outfile,bbox_inches='tight')

