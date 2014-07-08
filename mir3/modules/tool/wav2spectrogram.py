import argparse
import numpy

import mir3.data.metadata as md
import mir3.data.spectrogram as spectrogram
import mir3.module

#TODO: remove marsyas requirement

class Wav2Spectrogram(mir3.module.Module):
    def get_help(self):
        return """extract the spectrogram of a wav file"""

    def build_arguments(self, parser):
        parser.add_argument('-L','--dft-length', type=int, help="""length of the
                            DFT that will be calculated (default: value of
                            'window-length')""")
        parser.add_argument('-t','--spectrum-type', default='magnitude',
                            choices=['power', 'magnitude', 'decibels',
                            'logmagnitude', 'logmagnitude2'], help="""type of
                            spectrum generated. Possible values are 'power',
                            'magnitude', 'decibels', 'logmagnitude',
                            'logmagnitude2' (default: %(default)s)""")
        parser.add_argument('-l','--window-length', type=int, default=2048,
                            help="""window length, in samples (default:
                            %(default)s)""")
        parser.add_argument('-S','--window-shape', default='Hanning',
                            choices=['Bartlett', 'Blackman', 'Hamming',
                            'Hanning', 'Triangle'], help="""shape of the window.
                            Possible values are 'Bartlett', 'Blackman',
                            'Hamming', 'Hanning' or 'Triangle' (default:
                            %(default)s)""")
        parser.add_argument('-s','--window-step', type=int, default=1024,
                            help="""step, in samples, between windows (default:
                            %(default)s)""")

        parser.add_argument('infile', type=argparse.FileType('r'), help="""wav
                            file""")
        parser.add_argument('outfile', type=argparse.FileType('w'),
                            help="""spectrogram file""")

    def run(self, args):
        if args.dft_length is None:
            args.dft_length = args.window_length

        s = self.convert(args.infile,
                         args.window_length,
                         args.dft_length,
                         args.window_step,
                         args.window_shape,
                         args.spectrum_type)
        s.save(args.outfile)

    def convert(self, wav_file, window_length=2048, dft_length=2048,
                window_step=1024, window_shape='Hanning',
                spectrum_type='magnitude', save_metadata=True):
        """Converts a WAV file to a spectrogram.

        Currently we use Marsyas to do this stuff for us, so we accept any
        window or spectrum available there.

        Args:
            wav_file: handler for an open wav file.
            window_length: window length for dft, in samples. Default: 2048.
            dft_length: dft length used. Default: 2048.
            window_step: step between windows, in samples. Default: 1024.
            window_shape: shape for the filtered window. Default: 'Hanning'.
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
        s.metadata.sampling_configuration.window_shape  = window_shape
        s.metadata.sampling_configuration.spectrum_type = spectrum_type
        if save_metadata:
            s.metadata.input = md.FileMetadata(wav_file)

        self.__convert_with_marsyas(s, wav_file)

        return s

    def __convert_with_marsyas(self, s, wav_file):
        s.metadata.method = md.Metadata(name='Marsyas')

        # Initializes Marsyas
        net, snet = self.__configure_marsyas(s)

        # Configure the network to open the specified file
        net.updControl(snet["src"]+"/mrs_string/filename", wav_file.name)

        s.metadata.sampling_configuration.fs = \
                net.getControl(snet["src"] + "/mrs_real/osrate").to_real()
        s.metadata.sampling_configuration.ofs = \
                s.metadata.sampling_configuration.fs / \
                s.metadata.sampling_configuration.window_step

        # Sampling rate of the memory buffer
        memFs = s.metadata.sampling_configuration.ofs
        nSamples = \
                net.getControl(snet["src"] + "/mrs_natural/size").to_natural()

        if nSamples == 0:
            raise ValueError("File '%s' has no audio" % wav_file.name)

        dur = nSamples / s.metadata.sampling_configuration.fs
        memSize = int(dur * memFs)
        DFT_Len = 1 + (s.metadata.sampling_configuration.dft_length/2)

        s.data = numpy.zeros((DFT_Len, memSize))
        for i in range(memSize):
            net.tick()
            # Gather results to a numpy array
            s.data[:,i] = \
                    net.getControl("mrs_realvec/processedData").to_realvec()

        return s

    def __configure_marsyas(self, s):
        """Internal method. Shouldn't be called directly.
        """
        import mir3.lib.marsyas_util as marsyas_util

        # The memory was taken out of the network to improve the speed. The
        # windows will be recorded otherwise.
        spec_analyzer = ["Series/analysis", ["SoundFileSource/src",
                                             "Sum/summation", "Gain/gain",
                                             "ShiftInput/sft",
                                             "Windowing/win", "Spectrum/spk",
                                             "PowerSpectrum/pspk"]]
        net = marsyas_util.create(spec_analyzer)
        snet = marsyas_util.mar_refs(spec_analyzer)
        configuration = s.metadata.sampling_configuration

        net.updControl("mrs_natural/inSamples", configuration.window_step)
        # This will un-normalize the DFT
        net.updControl(snet["gain"]+"/mrs_real/gain",
                       configuration.window_length*1.0)
        net.updControl(snet["sft"]+"/mrs_natural/winSize",
                       configuration.window_length)
        net.updControl(snet["win"]+"/mrs_natural/zeroPadding",
                       configuration.dft_length-configuration.window_length)
        # "Hamming", "Hanning", "Triangle", "Bartlett", "Blackman"
        net.updControl(snet["win"]+"/mrs_string/type",
                       configuration.window_shape)
        # "power", "magnitude", "decibels", "logmagnitude" (for
        # 1+log(magnitude*1000), "logmagnitude2" (for 1+log10(magnitude)),
        # "powerdensity"
        net.updControl(snet["pspk"]+"/mrs_string/spectrumType",
                       configuration.spectrum_type)

        return net, snet
