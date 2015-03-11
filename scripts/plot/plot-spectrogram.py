
import argparse
import matplotlib.pyplot as plt

import mir3.data.spectrogram as spectrogram

def plot(input_filename, output_filename, size=(400,200)):
    """Plots the a spectrogram to an output file
    """
    s = spectrogram.Spectrogram()
    s.load(input_filename)

    d = s.data
    d = d/numpy.max(d)
    im = plt.imshow(d, aspect='auto', origin='lower', cmap=plt.cm.gray)
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (kHz)')
    fig = plt.gcf()
    width_inches = size[0]/80.0
    height_inches = size[1]/80.0
    fig.set_size_inches( (width_inches, height_inches) )
    plt.savefig(output_filename, bbox_inches='tight')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot a spectrogram')
    parser.add_argument('infile', help="""Input spectrogram file""")
    parser.add_argument('outfile', help="""Output figure file""")
    parser.add_argument('--width', type=int, default=400, help="""Output width (pixels).\
            Default: 400""")
    parser.add_argument('--height', type=int, default=200, help="""Output height (pixels).\
            Default: 200""")
    args = parser.parse_args()
    plot(args.infile, args.outfile, (args.width, args.height))




