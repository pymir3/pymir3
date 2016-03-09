import argparse
import numpy
import copy
import scipy.io.wavfile


import mir3.data.metadata as md
import mir3.data.spectrogram as spectrogram
import mir3.module

class Wav2Spectrogram(mir3.module.Module):
    def get_help(self):
        return """extract the spectrogram of a wav file"""

    def build_arguments(self, parser):
        parser.add_argument('-L','--dft-length', type=int, help="""length of the
                            DFT that will be calculated (default: value of
                            'window-length')""")
        parser.add_argument('-t','--spectrum-type', default='magnitude',
                            choices=['power', 'magnitude', 'log',
                            'sqrt'], help="""type of
                            spectrum generated (default: %(default)s)""")
        parser.add_argument('-l','--window-length', type=int, default=2048,
                            help="""window length, in samples (default:
                            %(default)s)""")
        #parser.add_argument('-S','--window-shape', default='Hanning',
        #                    choices=['Bartlett', 'Blackman', 'Hamming',
        #                    'Hanning', 'Triangle'], help="""shape of the window
        #                    (default: %(default)s)""")
        # TODO: Enable window shapes again.
        parser.add_argument('-s','--window-step', type=int, default=1024,
                            help="""step, in samples, between windows (default:
                            %(default)s)""")

        parser.add_argument('infile', type=argparse.FileType('rb'), help="""wav
                            file""")
        parser.add_argument('outfile', type=argparse.FileType('wb'),
                            help="""spectrogram file""")

    def run(self, args):
        if args.dft_length is None:
            args.dft_length = args.window_length

        s = self.convert(args.infile,
                         args.window_length,
                         args.dft_length,
                         args.window_step,
                         args.spectrum_type)
        s.save(args.outfile)

    def convert(self, wav_file, window_length=2048, dft_length=2048,
                window_step=1024,
                spectrum_type='magnitude', save_metadata=True):
        """Converts a WAV file to a spectrogram.

        Args:
            wav_file: handler for an open wav file.
            window_length: window length for dft, in samples. Default: 2048.
            dft_length: dft length used. Default: 2048.
            window_step: step between windows, in samples. Default: 1024.
            spectrum_type: type of spectrum extracted. Default: 'magnitude'.
            save_metadata: flag indicating whether the metadata should be
                           computed. Default: True.

        Returns:
            Spectrogram object.
        """
        # Sets metadata
        s = spectrogram.Spectrogram()
        s.metadata.sampling_configuration.window_length = window_length
        s.metadata.sampling_configuration.dft_length    = dft_length
        s.metadata.sampling_configuration.window_step   = window_step
        s.metadata.sampling_configuration.spectrum_type = spectrum_type


        if save_metadata:
            s.metadata.input = md.FileMetadata(wav_file)

        # Calculates data
        rate, data = scipy.io.wavfile.read(wav_file.name)

        data = data.astype(numpy.float)

        data /= numpy.max(numpy.abs(data)) # Normalization to -1/+1 range

        if data.ndim > 1:
            data = numpy.sum(data, axis=1)

        s.metadata.min_time = 0.0
        s.metadata.min_freq = 0.0
        s.metadata.max_time = len(data) / float(rate)
        s.metadata.max_freq = 0.5 * rate

        s.metadata.sampling_configuration.fs = rate
        s.metadata.sampling_configuration.ofs = \
                s.metadata.sampling_configuration.fs / \
                float(s.metadata.sampling_configuration.window_step)

        nSamples = len(data)

        if nSamples == 0:
            raise ValueError("File '%s' has no audio" % wav_file.name)

        #print data[0:32]
        #print numpy.abs(numpy.fft.rfft(data[0:32]))
        #print numpy.abs(numpy.fft.rfft(data[32:64]))

        window = numpy.hanning(window_length)

        nframes = (len(data) / window_step) - 1
        buffered_data = numpy.zeros( (window_length, nframes) )
        for k in xrange(nframes):
            this_start = k * window_step
            this_end = this_start + window_length
            buffered_data[:,k] = (data[this_start:this_end] * window)

        #buffered_data = numpy.array(buffered_data).T
        #buffered_data = buffered_data * numpy.sqrt(window_length)

        Pxx = numpy.abs(numpy.fft.rfft(buffered_data,\
                            n = dft_length,\
                            axis = 0))

        #print Pxx[:,0]

        #Pxx, freqs, bins, im = pylab.specgram(data,\
        #                NFFT=s.metadata.sampling_configuration.window_length,\
        #                Fs=s.metadata.sampling_configuration.fs,\
        #                window=pylab.window_hanning,\
        #                noverlap=s.metadata.sampling_configuration.window_length-\
        #                s.metadata.sampling_configuration.window_step,
        #                pad_to=s.metadata.sampling_configuration.dft_length)

        if s.metadata.sampling_configuration.spectrum_type == 'sqrt':
            Pxx = numpy.sqrt(Pxx)

        if s.metadata.sampling_configuration.spectrum_type == 'power':
            Pxx = Pxx ** 2

        if s.metadata.sampling_configuration.spectrum_type == 'log':
            Pxx = numpy.log10(numpy.sqrt(Pxx) + 10**(-6))

        s.data = copy.deepcopy(Pxx)
        # print type(s.data), s.data.shape
        #pylab.show()

        return s
