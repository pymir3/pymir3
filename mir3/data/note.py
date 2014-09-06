import copy
import math

import mir3.data.blank as blank
import mir3.data.data_object as do
import mir3.data.metadata as md

class Note(do.DataObject):
    """A generic representation of a note.

    For now we only allow notes associated with frequencies, so other
    instruments, like drums, can't be properly represented.

    Metadata available:
        -ref_freq: frequency associated with reference midi. If freq ==
                   ref_freq, then pitch = ref_midi. Default: 440.0 (A4).
        -ref_midi: pitch associated with reference frequency. If pitch ==
                   ref_midi, then freq = ref_freq. Default: 69.0 (A4).

    Data available:
        -duration: total duration of the note. Call reset_duration() to
                   recompute.
        -freq: note's frequency.
        -onset: note's start.
        -offset: note's end.
        -pitch: note's logarithmic representation using ref_freq and ref_midi.
    """

    # Frequency, in Hz, of the note A4. If you change this, everything in your
    # code will consider other temperament
    freq_A4 = 440.0

    # Pitch, in the MIDI scale, of the reference note A4. If you change this,
    # you will transpose your whole program.
    midi_A4 = 69.0

    # Ratio of frequencies between notes in the equal-temperament scale
    freq_ratio = math.pow(2, 1.0/12.0)

    # Names of the pitch classes that can be handled
    note_names_sharp = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A",
                        "A#", "B"]
    note_names_flat  = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A",
                        "Bb", "B"]
    white_notes = ["A", "B", "C", "D", "E", "F", "G"]

    def __init__(self, onset=0, offset=0, pitch=None, name=None, freq=None,
                 ref_freq=freq_A4, ref_midi=midi_A4):
        """Creates a note.

        At least of of pitch, name and freq must be set or an exception will be
        raisen, as we can't identify the node. If more than one is set, we
        first check pitch, then name and then freq.

        Offset must occur at onset or after. Otherwise an exception will occur.

        Args:
            onset: note's start.
            offset: note's end.
            pitch: note's pitch. Default: None.
            name: note's name. Default: None.
            freq: note's frequency. Default: None.
            ref_freq: reference frequency. Defaul: A4.
            ref_midi: reference pitch. Defaul: A4.

        Raises:
            ValuError: either onset is after offset or couldn't determine which
                       note to create.
        """
        # Sanity checking
        if onset > offset:
            raise ValueError("Onset cannot be after offset.")

        # Metadata stores references for type conversion
        super(Note, self).__init__(
                md.Metadata(ref_freq=float(ref_freq),
                            ref_midi=ref_midi))

        self.data = blank.Blank(duration=float(offset)-float(onset),
                                onset=float(onset),
                                offset=float(offset),
                                freq=0.,
                                pitch=0)

        # Chooses source of data
        if pitch is not None:
            self.from_pitch(pitch)
        elif name is not None:
            self.from_name(name)
        elif freq is not None:
            self.from_freq(freq)
        else:
            raise ValueError("A pitch, name or frequency must be specified.")

    def reset_duration(self):
        """Computes note duration.

        Sets duration to offset - onset. This must be called every time onset or
        offset is set for consistency.

        Returns:
            self
        """
        self.data.duration = self.data.offset - self.data.onset

        return self

    def transpose(self, ammount=0):
        """Offsets note's pitch.

        Increases note's pitch by the ammount given.

        Args:
            ammount: number of pitches to change.

        Returns:
            self
        """
        self.from_pitch(self.data.pitch + ammount)

        return self

    def from_pitch(self, pitch):
        """Sets note's pitch.

        Computes the associated frequency and store it and the pitch.

        Args:
            pitch: desired pitch.

        Returns:
            self
        """
        self.data.pitch = pitch
        self.data.freq = self.metadata.ref_freq * \
                         (2**((pitch-self.metadata.ref_midi)/12.0))

        return self

    def from_freq(self, freq, fixed_pitches=True):
        """Sets note's frequency.

        Computes the associated pitch and store it and the frequency. The pitch
        is rounded to the nearest integer if fixed_pitches is true.

        Args:
            freq: desired frequency.
            fixed_pitches: if True, pitch is rounded to nearest integer.
                           Default: True.

        Returns:
            self
        """
        self.data.freq = freq
        self.data.pitch = self.metadata.ref_midi + \
                          12.0*math.log(1.0*freq/self.metadata.ref_freq,2.0)

        if fixed_pitches:
            self.data.pitch = int(round(self.data.pitch))

        return self

    def to_name(self, use_flat=True):
        """Build note's name.

        Based on the stored pitch, creates a name for the note. The pitch is
        rounded to the nearest integer. If use_flat is true, we use flat
        notation for semi-notes, using sharp otherwise.

        Args:
            use_flat: if True, semi-notes are flat. Default: True.

        Returns:
            self
        """
        # Gets note class and octave
        pitch = int(round(self.data.pitch))
        octave = int(pitch/12)-1
        pclass = (pitch%12)

        if use_flat:
            return Note.note_names_flat[pclass]+str(octave)
        else:
            return Note.note_names_sharp[pclass]+str(octave)

    def from_name(self, name):
        """Sets note's pitch and frequency.

        Uses the name provided to compute the associated pitch and set it. Both
        flat and sharp notations are provided.

        Args:
            name: string with the note's name.

        Returns:
            self

        Raises:
            ValueError: the name provided is an invalid note name.
        """
        # As we'll change the name, make a copy
        name = copy.deepcopy(name)

        # If the name is flat, turn it into sharp
        if name[1] == 'b':
            name = Note.white_notes[Note.white_notes.index(name[0])-1] + \
                                    "#"+name[2]

        name = name.upper()

        # Split note name and octave
        if name[1]=="#":
            pclass = name[0:2]
            octave = name[2:]
        else:
            pclass = name[0:1]
            octave = name[1:]

        # Only check for sharp as we removed the flats
        if pclass in Note.note_names_sharp:
            m = Note.note_names_sharp.index(pclass)
        else:
            raise ValueError("Invalid note name.")

        # Octave must be an integer
        try:
            octave = int(octave)
        except ValueError:
            raise ValueError("Invalid note name.")

        # Computes the associated pitch
        self.from_pitch(int(((1+octave)*12)+m))

    def __lt__(self, other):
        """Compares two notes.

        If another type of object is used, an exception occurs. Sorting order:
        onset, offset, pitch

        Args:
            other: note to compare.

        Returns:
            Flag indicating if self should occur befor other.

        Raises:
            NotImplementedError: tried to compare a Note with something else.
        """
        if not isinstance(other, Note):
            raise NotImplementedError("Tried to compare a Note with something "
                                      "else.")

        if self.data.onset != other.data.onset:
            return self.data.onset < other.data.onset

        elif self.data.offset != other.data.offset:
            return self.data.offset < other.data.offset

        else:
            return self.data.pitch < other.data.pitch
