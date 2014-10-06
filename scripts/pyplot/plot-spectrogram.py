# Plots a spectrogram as a figure. This should be a good app to 

import argparse
import matplotlib.pyplot as plt
import numpy
import mir3.data.spectrogram as spectrogram

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help="""spectrogram file""")
    parser.add_argument('outfile', help="""target image file""")
    parser.add_argument('-f','--minimum_frequency', 
        default=0, help="""Minimum frequency (Hz) to plot""")
    parser.add_argument('-F','--maximum_frequency', 
        default=2000, help="""Maximum frequency (Hz) to plot""")
    parser.add_argument('-t','--minimum_time', 
        default=0, help="""Minimum time (s) to plot""")
    parser.add_argument('-T','--maximum_time', 
        default=None, help="""Maximum time (s) to plot""")
    parser.add_argument('-W', '--width',
        default=400, help="""Plot width (px)""")
    parser.add_argument('-H', '--height',
        default=200, help="""Plot height (px)""")

    args = parser.parse_args()
    
    s = spectrogram.Spectrogram()
    s = s.load(open(args.infile))

    maxK = s.freq_bin(args.maximum_frequency)
    minK = s.freq_bin(args.minimum_frequency)
    if args.maximum_time is not None:
        maxT = s.time_bin(args.maximum_time)

    else:
        maxT = s.data.shape[1]

    maxTs = maxT / s.metadata.sampling_configuration.ofs
    minT = s.time_bin(args.minimum_time)
    
    out = s.data[minK:maxK, minT:maxT]
    out = out/numpy.max(out)
    out = 1-out
    
    im=plt.imshow(out, aspect='auto', origin='lower', cmap=plt.cm.gray,
        extent=[args.minimum_time, maxTs,
                args.minimum_frequency/1000, args.maximum_frequency/1000])
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (kHz)')
    fig = plt.gcf()

    size = (args.width, args.height)
    width_inches = size[0]/80.0
    height_inches = size[1]/80.0
    fig.set_size_inches((width_inches,height_inches))

    plt.savefig(args.outfile,bbox_inches='tight')

