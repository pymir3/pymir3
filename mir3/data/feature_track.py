import mir3.data.data_object as do
import mir3.data.metadata as md

class FeatureTrack(do.DataObject):
    """Stores a feature track from an audio track.
    """

    def __init__(self):
        super(FeatureTrack, self).__init__(md.Metadata(feature="Energy",
                                                       filename="",
                                                       input_metadata=None,
                        sampling_configuration=md.Metadata(
                            dft_length=1024, fs=None, ofs=None,
                            spectrum_type='magnitude', window_length=1024,
                            window_shape='Hanning', window_step=1024)))

