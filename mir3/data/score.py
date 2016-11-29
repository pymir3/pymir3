import mir3.data.data_object as do
import mir3.data.metadata as md
import mir3.data.note as note

class Score(do.DataObject):
    """Set of notes from an instrument.

    Any source of notes, either from the user or some algorithm, creates a score
    so that evaluation algorithms can compare them freely. We have sets of tools
    to convert common formats, like labels or midi to our format.

    Metadata available information:
        -instrument: name of the instrument represented in the score.
        -method_metadata: metadata from the method that created the score. It
                          has at least one information named 'type' that can be:
            -algorithm if the score was created by some algorithm, in which case
             more information about the algorithm is stored;
            -label if the score was converted from a label;
            -midi if the score was converted from a midi.
        -input: file metadata for the source of this score.

    Data available: list of Notes on the score.
    """

    def __init__(self):
        super(Score, self).__init__(
                md.Metadata(instrument=None,
                            method_metadata=None,
                            input=None,
                            input_metadata=None))
        self.data = []

    def append(self, sequence):
        """Adds notes to the score.

        The object to be added can be a Note, another Score or a list. If it's a
        list, we iterate over their objects and append them. This method is
        destructive in case of an exception, because the data may already have
        been modified.

        Args:
            sequence: a Note, Score or list to append.

        Returns:
            self

        Raises:
            ValueError: tried to append an invalid object.
        """
        if isinstance(sequence,note.Note):
            toAppend = [sequence]
        elif isinstance(sequence,Score):
            toAppend = sequence.data
        elif isinstance(sequence,list):
            for v in sequence:
                self.append(v)
            toAppend = []
        else:
            raise ValueError("Tried to add invalid object to a score.")

        self.data += toAppend

        return self

    def sort(self):
        """Sorts the notes to allow faster comparison between scores.

        Returns:
            self
        """
        self.data.sort()

        return self

    def get_timespan(self):
        """Gets the range of time represented.

        Returns:
            Tuple of (start, end) of score's notes.
        """
        if len(self.data) == 0:
            return 0., 0.

        t_start = min([n.data.onset for n in self.data])
        t_end = max([n.data.offset for n in self.data])
        return t_start, t_end

    def get_active_notes(self, time):
        """Gets the notes active at a given time.

        Compare notes' onsets and offsets and return a list of those active at
        the time given.

        Args:
            time: instant of time.

        Returns:
            List of notes active.
        """
        return [note for note in self.data if note.data.onset <= time and
                                              note.data.offset >= time]

    def get_active_notes_list(self, time_list):
        """Gets the notes active at the times in a list.

        Assumes that the times in the list are sorted to increase speed. They
        should be as tight in the timespan as possible.

        The returned list has another list for each time.

        Args:
            time_list: list of times.

        Returns:
            List of lists of notes active.
        """
        # Every note is valid at first
        valid_notes = self.data
        ret = []

        for time in time_list:
            # We can remove notes with offset smalled than the current time, as
            # the time is increasing
            valid_notes = [note for note in valid_notes \
                    if note.data.offset >= time]

            # Only need to check if onset already happened, as offset is in the
            # future already
            ret.append([note for note in valid_notes \
                    if note.data.onset <= time])

        return ret
