import argparse
import numpy
import copy
import scipy.io.wavfile
import scipy.signal
import scipy.fftpack as fft
import wave
import os
import six
import mir3.data.metadata as md
import mir3.data.spectrogram as spectrogram
import mir3.module
import tempfile
import subprocess
import gc

MAX_MEM_BLOCK = 2**8 * 2**10

class DummyArray(object):
    """Dummy object that just exists to hang __array_interface__ dictionaries
    and possibly keep alive a reference to a base array.
    """

    def __init__(self, interface, base=None):
        self.__array_interface__ = interface
        self.base = base

def magphase(D):
    """Separate a complex-valued spectrogram D into its magnitude (S)
    and phase (P) components, so that `D = S * P`.


    Parameters
    ----------
    D       : np.ndarray [shape=(d, t), dtype=complex]
        complex-valued spectrogram


    Returns
    -------
    D_mag   : np.ndarray [shape=(d, t), dtype=real]
        magnitude of `D`
    D_phase : np.ndarray [shape=(d, t), dtype=complex]
        `exp(1.j * phi)` where `phi` is the phase of `D`

    """

    mag = numpy.abs(D)
    phase = numpy.exp(1.j * numpy.angle(D))

    return mag, phase

def pad_center(data, size, axis=-1, **kwargs):
    '''Wrapper for np.pad to automatically center an array prior to padding.
    This is analogous to `str.center()`

    Parameters
    ----------
    data : np.ndarray
        Vector to be padded and centered

    size : int >= len(data) [scalar]
        Length to pad `data`

    axis : int
        Axis along which to pad and center the data

    kwargs : additional keyword arguments
      arguments passed to `np.pad()`

    Returns
    -------
    data_padded : np.ndarray
        `data` centered and padded to length `size` along the
        specified axis

    See Also
    --------
    numpy.pad
    '''

    kwargs.setdefault('mode', 'constant')

    n = data.shape[axis]

    lpad = int((size - n) // 2)

    lengths = [(0, 0)] * data.ndim
    lengths[axis] = (lpad, int(size - n - lpad))

    if lpad < 0:
        print (('Target size ({:d}) must be '
                                     'at least input size ({:d})').format(size,
                                                                          n))
        exit(1)

    return numpy.pad(data, lengths, **kwargs)


def as_strided(x, shape=None, strides=None):
    """ Make an ndarray from the given array with the given shape and strides.
    """
    interface = dict(x.__array_interface__)
    if shape is not None:
        interface['shape'] = tuple(shape)
    if strides is not None:
        interface['strides'] = tuple(strides)
    array = numpy.asarray(DummyArray(interface, base=x))
    # Make sure dtype is correct in case of custom dtype
    if array.dtype.kind == 'V':
        array.dtype = x.dtype
    return array


def frame(y, frame_length=2048, hop_length=512):
    '''Slice a time series into overlapping frames.

    This implementation uses low-level stride manipulation to avoid
    redundant copies of the time series data.

    Parameters
    ----------
    y : np.ndarray [shape=(n,)]
        Time series to frame. Must be one-dimensional and contiguous
        in memory.

    frame_length : int > 0 [scalar]
        Length of the frame in samples

    hop_length : int > 0 [scalar]
        Number of samples to hop between frames

    Returns
    -------
    y_frames : np.ndarray [shape=(frame_length, N_FRAMES)]
        An array of frames sampled from `y`:
        `y_frames[i, j] == y[j * hop_length + i]`

    '''


    if hop_length < 1:
        print('Invalid hop_length: {:d}'.format(hop_length))
        exit(1)

    if not y.flags['C_CONTIGUOUS']:
        print ('Input buffer must be contiguous.')
        exit(1)

    #valid_audio(y)

    # Compute the number of frames that will fit. The end may get truncated.
    n_frames = 1 + int((len(y) - frame_length) / hop_length)

    if n_frames < 1:
        print('Buffer is too short (n={:d})'
                                    ' for frame_length={:d}'.format(len(y),
                                                                    frame_length))
    # Vertical stride is one sample
    # Horizontal stride is `hop_length` samples
    y_frames = as_strided(y, shape=(frame_length, n_frames),
                          strides=(y.itemsize, hop_length * y.itemsize))
    return y_frames

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

    def stft(self, y, n_fft=2048, hop_length=None, win_length=None, window=None,
             center=True, dtype=numpy.complex64):
        """Short-time Fourier transform (STFT)

        Implementation based upon librosa:
            https://github.com/bmcfee/librosa/blob/master/librosa/core/spectrum.py

        Returns a complex-valued matrix D such that
            `np.abs(D[f, t])` is the magnitude of frequency bin `f`
            at frame `t`

            `np.angle(D[f, t])` is the phase of frequency bin `f`
            at frame `t`

        Parameters
        ----------
        y : np.ndarray [shape=(n,)], real-valued
            the input signal (audio time series)

        n_fft : int > 0 [scalar]
            FFT window size

        hop_length : int > 0 [scalar]
            number audio of frames between STFT columns.
            If unspecified, defaults `win_length / 4`.

        win_length  : int <= n_fft [scalar]
            Each frame of audio is windowed by `window()`.
            The window will be of length `win_length` and then padded
            with zeros to match `n_fft`.

            If unspecified, defaults to ``win_length = n_fft``.

        window : None, function, np.ndarray [shape=(n_fft,)]
            - None (default): use an asymmetric Hann window
            - a window function, such as `scipy.signal.hanning`
            - a vector or array of length `n_fft`

        center      : boolean
            - If `True`, the signal `y` is padded so that frame
              `D[:, t]` is centered at `y[t * hop_length]`.
            - If `False`, then `D[:, t]` begins at `y[t * hop_length]`

        dtype       : numeric type
            Complex numeric type for `D`.  Default is 64-bit complex.


        Returns
        -------
        D : np.ndarray [shape=(1 + n_fft/2, t), dtype=dtype]
            STFT matrix

        """

        # By default, use the entire frame
        if win_length is None:
            win_length = n_fft

        # Set the default hop, if it's not already specified
        if hop_length is None:
            hop_length = int(win_length / 4)

        if window is None:
            # Default is an asymmetric Hann window
            fft_window = scipy.signal.hann(win_length, sym=False)

        elif six.callable(window):
            # User supplied a window function
            fft_window = window(win_length)

        else:
            # User supplied a window vector.
            # Make sure it's an array:
            fft_window = numpy.asarray(window)

            # validate length compatibility
            if fft_window.size != n_fft:
                print('Size mismatch between n_fft and len(window)')
                exit(1)

        # Pad the window out to n_fft size
        fft_window = pad_center(fft_window, n_fft)

        # Reshape so that the window can be broadcast
        fft_window = fft_window.reshape((-1, 1))

        # Pad the time series so that frames are centered
        if center:
            #util.valid_audio(y)
            y = numpy.pad(y, int(n_fft // 2), mode='reflect')

        # Window the time series.
        y_frames = frame(y, frame_length=n_fft, hop_length=hop_length)

        # Pre-allocate the STFT matrix
        stft_matrix = numpy.empty((int(1 + n_fft // 2), y_frames.shape[1]),
                               dtype=dtype,
                               order='F')

        # how many columns can we fit within MAX_MEM_BLOCK?
        n_columns = int(MAX_MEM_BLOCK / (stft_matrix.shape[0] *
                                              stft_matrix.itemsize))

        for bl_s in range(0, stft_matrix.shape[1], n_columns):
            bl_t = min(bl_s + n_columns, stft_matrix.shape[1])

            # RFFT and Conjugate here to match phase from DPWE code
            stft_matrix[:, bl_s:bl_t] = fft.fft(fft_window *
                                                y_frames[:, bl_s:bl_t],
                                                axis=0)[:stft_matrix.shape[0]].conj()

        return stft_matrix

    def decode_mp3(self, mp3filename):
        """Decodes an MP3 to a temporary WAV file and returns its full path.
        The temporary file must be manually deleted after being used.

        """

        print("Decoding MP3: %s" % mp3filename)

        (wavfile, wav_filename) = tempfile.mkstemp(suffix=".wav")

        os.close(wavfile)

        sox = ["sox", mp3filename, "-c", "1", wav_filename]

        errcode = subprocess.call(sox)

        if errcode > 0:
            print("error decoding %s to %s (sox returned code %d)" % (mp3filename, wav_filename, errcode) )

        return open(wav_filename, "rb")


    def load_audio(self, audiofile, mono=True, fs=44100, zero_pad_resampling=False):
        """Load audio file into numpy array
        Supports 24-bit wav-format, and flac audio through librosa.
        Parameters
        ----------
        filename:  str
            Path to audio file
        mono : bool
            In case of multi-channel audio, channels are averaged into single channel.
            (Default value=True)
        fs : int > 0 [scalar]
            Target sample rate, if input audio does not fulfil this, audio is resampled.
            (Default value=44100)
        Returns
        -------
        audio_data : numpy.ndarray [shape=(signal_length, channel)]
            Audio
        sample_rate : integer
            Sample rate

        from: https://github.com/TUT-ARG/DCASE2016-baseline-system-python/blob/master/src/files.py
        """

        if isinstance(audiofile, basestring):
            audiofile = open(audiofile, "rb")

        file_base, file_extension = os.path.splitext(audiofile.name)

        if file_extension == '.mp3':
            audiofilename = audiofile.name
            audiofile.close()
            audiofile = self.decode_mp3(audiofilename)

        audio_file = wave.open(audiofile)

        # Audio info
        sample_rate = audio_file.getframerate()
        sample_width = audio_file.getsampwidth()
        number_of_channels = audio_file.getnchannels()
        number_of_frames = audio_file.getnframes()

        # Read raw bytes
        data = audio_file.readframes(number_of_frames)
        audio_file.close()

        # Convert bytes based on sample_width
        num_samples, remainder = divmod(len(data), sample_width * number_of_channels)
        if remainder > 0:
            raise ValueError('The length of data is not a multiple of sample size * number of channels.')
        if sample_width > 4:
            raise ValueError('Sample size cannot be bigger than 4 bytes.')

        if sample_width == 3:
            # 24 bit audio
            a = numpy.empty((num_samples, number_of_channels, 4), dtype=numpy.uint8)
            raw_bytes = numpy.fromstring(data, dtype=numpy.uint8)
            a[:, :, :sample_width] = raw_bytes.reshape(-1, number_of_channels, sample_width)
            a[:, :, sample_width:] = (a[:, :, sample_width - 1:sample_width] >> 7) * 255
            audio_data = a.view('<i4').reshape(a.shape[:-1]).T
        else:
            # 8 bit samples are stored as unsigned ints; others as signed ints.
            dt_char = 'u' if sample_width == 1 else 'i'
            a = numpy.fromstring(data, dtype='<%s%d' % (dt_char, sample_width))
            audio_data = a.reshape(-1, number_of_channels).T

        if mono:
            # Down-mix audio
            audio_data = numpy.mean(audio_data, axis=0)

        # Convert int values into float
        audio_data = audio_data / float(2 ** (sample_width * 8 - 1) + 1)

        # Resample
        if fs != sample_rate:
            #zero pad to nearest power of two to improve resampling performance
            if zero_pad_resampling:
                n = len(audio_data)
                y = int(numpy.floor(numpy.log2(n)))
                nextpow2 = numpy.power(2, y + 1)
                audio_data = numpy.pad(audio_data, ((nextpow2 - n), (0)), mode='constant')

            audio_data = scipy.signal.resample(audio_data, len(audio_data) * (float(fs) / sample_rate) )
            sample_rate = fs

        audiofile.close()
        audio_file.close()

        if file_extension == '.mp3':
            os.unlink(audiofile.name)

        return sample_rate, audio_data

        #return None, None

    def convert(self, wav_file, window_length=2048, dft_length=2048,
                window_step=1024,
                spectrum_type='magnitude', save_metadata=True, wav_rate=None, wav_data=None):

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

        if wav_data is None:
            from_data = False
        else:
            from_data = True

        if isinstance(wav_file, basestring):
            wav_file = open(wav_file, "rb")

        if save_metadata:
            s.metadata.input = md.FileMetadata(wav_file)

        # Calculates data
        if not from_data:
            rate, data = self.load_audio(wav_file)
        else:
            rate = wav_rate
            data = wav_data

        #data /= numpy.max(numpy.abs(data)) # Normalization to -1/+1 range

        data -= numpy.mean(data)
        data /= numpy.var(data)**(0.5)

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

        window = scipy.signal.hamming(dft_length, sym=False)

        #magnitude spectrum is the absolute value (real part) of the complex spectrum
        magnitude_spectrum = numpy.abs(self.stft(data, n_fft=dft_length,
            hop_length=window_step, win_length=window_length, window=window,
            center = True))

        if s.metadata.sampling_configuration.spectrum_type == 'sqrt':
            magnitude_spectrum = numpy.sqrt(magnitude_spectrum)

        if s.metadata.sampling_configuration.spectrum_type == 'power':
            magnitude_spectrum = magnitude_spectrum ** 2

        if s.metadata.sampling_configuration.spectrum_type == 'log':
            magnitude_spectrum = numpy.log10(numpy.sqrt(magnitude_spectrum) + 10**(-6))

        if s.metadata.sampling_configuration.spectrum_type == 'db':
            magnitude_spectrum = 20 * numpy.log10(magnitude_spectrum + numpy.finfo(numpy.float).eps)

        s.data = copy.deepcopy(magnitude_spectrum)
        # print type(s.data), s.data.shape
        #pylab.show()

        return s

    # def convert(self, wav_file, window_length=2048, dft_length=2048,
    #             window_step=1024,
    #             spectrum_type='magnitude', save_metadata=True):
    #     """Converts a WAV file to a spectrogram.
    #
    #     Args:
    #         wav_file: handler for an open wav file.
    #         window_length: window length for dft, in samples. Default: 2048.
    #         dft_length: dft length used. Default: 2048.
    #         window_step: step between windows, in samples. Default: 1024.
    #         spectrum_type: type of spectrum extracted. Default: 'magnitude'.
    #         save_metadata: flag indicating whether the metadata should be
    #                        computed. Default: True.
    #
    #     Returns:
    #         Spectrogram object.
    #     """
    #     # Sets metadata
    #     s = spectrogram.Spectrogram()
    #     s.metadata.sampling_configuration.window_length = window_length
    #     s.metadata.sampling_configuration.dft_length    = dft_length
    #     s.metadata.sampling_configuration.window_step   = window_step
    #     s.metadata.sampling_configuration.spectrum_type = spectrum_type
    #
    #
    #     if save_metadata:
    #         s.metadata.input = md.FileMetadata(wav_file)
    #
    #     # Calculates data
    #     #rate, data = scipy.io.wavfile.read(wav_file.name)
    #     #data = data.astype(numpy.float)
    #
    #     rate, data = self.load_audio(wav_file)
    #
    #     #data /= numpy.max(numpy.abs(data)) # Normalization to -1/+1 range
    #
    #     data -= numpy.mean(data)
    #     data /= numpy.var(data)**(0.5)
    #
    #     if data.ndim > 1:
    #         data = numpy.sum(data, axis=1)
    #
    #     s.metadata.min_time = 0.0
    #     s.metadata.min_freq = 0.0
    #     s.metadata.max_time = len(data) / float(rate)
    #     s.metadata.max_freq = 0.5 * rate
    #
    #     s.metadata.sampling_configuration.fs = rate
    #     s.metadata.sampling_configuration.ofs = \
    #             s.metadata.sampling_configuration.fs / \
    #             float(s.metadata.sampling_configuration.window_step)
    #
    #     nSamples = len(data)
    #
    #     if nSamples == 0:
    #         raise ValueError("File '%s' has no audio" % wav_file.name)
    #
    #     #print data[0:32]
    #     #print numpy.abs(numpy.fft.rfft(data[0:32]))
    #     #print numpy.abs(numpy.fft.rfft(data[32:64]))
    #
    #     window = numpy.hanning(window_length)
    #
    #     nframes = (len(data) / window_step) - 1
    #     buffered_data = numpy.zeros( (window_length, nframes) )
    #     for k in xrange(nframes):
    #         this_start = k * window_step
    #         this_end = this_start + window_length
    #         buffered_data[:,k] = (data[this_start:this_end] * window)
    #
    #     #buffered_data = numpy.array(buffered_data).T
    #     #buffered_data = buffered_data * numpy.sqrt(window_length)
    #
    #     Pxx = numpy.abs(numpy.fft.rfft(buffered_data,\
    #                         n = dft_length,\
    #                         axis = 0))
    #
    #     #print Pxx[:,0]
    #
    #     #Pxx, freqs, bins, im = pylab.specgram(data,\
    #     #                NFFT=s.metadata.sampling_configuration.window_length,\
    #     #                Fs=s.metadata.sampling_configuration.fs,\
    #     #                window=pylab.window_hanning,\
    #     #                noverlap=s.metadata.sampling_configuration.window_length-\
    #     #                s.metadata.sampling_configuration.window_step,
    #     #                pad_to=s.metadata.sampling_configuration.dft_length)
    #
    #     if s.metadata.sampling_configuration.spectrum_type == 'sqrt':
    #         Pxx = numpy.sqrt(Pxx)
    #
    #     if s.metadata.sampling_configuration.spectrum_type == 'power':
    #         Pxx = Pxx ** 2
    #
    #     if s.metadata.sampling_configuration.spectrum_type == 'log':
    #         Pxx = numpy.log10(numpy.sqrt(Pxx) + 10**(-6))
    #
    #     s.data = copy.deepcopy(Pxx)
    #     # print type(s.data), s.data.shape
    #     #pylab.show()
    #
    #     return s
