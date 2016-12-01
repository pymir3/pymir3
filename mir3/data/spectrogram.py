import mir3.data.data_object as do
import mir3.data.metadata as md

class Spectrogram(do.DataObject):
    """Interface between wav files and all other algorithms in PyMIR3.

    The metadata provides information about the sampling method and the input
    used to create the spectrogram.

    Metadata available information:
        -input: wav input metadata. Default: None.
        -method: details about the method used.
        -min_freq: minimum frequency represented in the spectrogram. Default: 0.
        -min_time: minimum time represented in the spectrogram. Default: 0.
        -max_freq: maximum frequency represented in the spectrogram.
        -max_time: maximum time represented in the spectrogram.
        -sampling_configuration: metadata with sampling details.
            -dft_length: size of the dft. Default: 1024.
            -fs: sampling frequency. Default: None.
            -ofs: output sampling frequency. Should be given by fs/window_step.
                  Default: None.
            -spectrum_type: information colected from the spectrum and stored in
                            this object. Default: 'magnitude'.
            -window_length: size of the window used. Default: 1024.
            -window_shape: shape used in window. Default: 'Hanning'.
            -window_step: step used for the window. Default: 1024.

    Data available: spectrogram array, where each row is a frequency bin and
                    each column is a time step.
    """

    def __init__(self):
        super(Spectrogram, self).__init__(
            md.Metadata(input=None,
                        input_metadata=None,
                        method=None,
                        min_freq=0.,
                        min_time=0.,
                        max_freq=0.,
                        max_time=0.,
                        sampling_configuration=md.Metadata(
                            dft_length=1024,
                            fs=None,
                            ofs=None,
                            spectrum_type='magnitude',
                            window_length=1024,
                            window_shape='Hanning',
                            window_step=1024)))

    def freq_bin(self, frequency):
        """Computes which bin a certain frequency belongs.

        Based on the configuration provided, returns the discrete frequency bin
        to which the frequency is assigned. If it's out of range, then returns
        the corresponding extreme bin.

        Args:
            frequency: Frequency to be evaluated.

        Returns:
            The bin associated with the frequency.
        """
        if frequency == float('inf'):
            return self.data.shape[0]-1

        freq_scale = float(self.metadata.sampling_configuration.dft_length) / \
                     self.metadata.sampling_configuration.fs

        # Rounds using floor
        freq_bin = int((frequency - self.metadata.min_freq) * freq_scale)

        if freq_bin < 0:
            freq_bin = 0
        elif freq_bin >= self.data.shape[0]:
            freq_bin = self.data.shape[0]-1
        return freq_bin

    def freq_range(self, bin):
        """Computes the frequency range in a bin.

        Based on the configuration provided, return the range of frequencies
        assigned to a certain bin.

        Args:
            bin: Bin to be evaluated.

        Returns:
            Tuple containing the lower and upper frequencies, respectively.
        """
        freq_scale = float(self.metadata.sampling_configuration.dft_length) / \
                     self.metadata.sampling_configuration.fs

        lower = bin / freq_scale + self.metadata.min_freq;
        upper = (bin+1) / freq_scale + self.metadata.min_freq;

        return lower, upper

    def time_bin(self, time):
        """Computes which bin a certain time belongs.

        Based on the configuration provided, returns the discrete time bin to
        which the time is assigned.

        Args:
            time: Time to be evaluated.

        Returns:
            The bin associated with the time.
        """
        if time == float('inf'):
            return self.data.shape[1]-1

        time_scale = self.metadata.sampling_configuration.ofs

        # Rounds using conversion to int
        time_bin = int((time - self.metadata.min_time) * time_scale)

        if time_bin < 0:
            time_bin = 0
        elif time_bin >= self.data.shape[1]:
            time_bin = self.data.shape[1]-1
        return time_bin

    def time_range(self, bin):
        """Computes the time range in a bin.

        Based on the configuration provided, return the range of times assigned
        to a certain bin.

        Args:
            bin: Bin to be evaluated.

        Returns:
            Tuple containing the lower and upper times, respectively.
        """
        time_scale = 1.0*self.metadata.sampling_configuration.ofs

        lower = bin / time_scale + self.metadata.min_time;
        upper = (bin+1) / time_scale + self.metadata.min_time;

        return lower, upper
