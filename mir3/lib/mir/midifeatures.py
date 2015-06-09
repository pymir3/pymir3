# Symbolic feature extraction from sequences of notes
# WARNING: sort your note sequences according to onset time before using these
# functions!

import numpy

def range(sequence):
    """Returns the note rance in a tuplet (min_note, max_note)"""
    min_pitch = 999
    max_pitch = 0
    for note in sequence:
        if note.data.pitch < min_pitch:
            min_pitch = note.data.pitch
        if note.data.pitch > max_pitch:
            max_pitch = note.data.pitch

    return (min_pitch, max_pitch)

def pitchclass_histogram(sequence, duration=False):
    """Returns a pitch-class histogram of the sequence

    0 represents C, 1 represents C# and so on.
    If duration is set to True, then the histogram will consider the note
    durations (default is considering each occurence as a count)
    """
    histogram = numpy.zeros(12)
    for note in sequence:
        pitchclass = note.data.pitch % 12
        if duration is True:
            histogram[pitchclass] += note.data.offset - note.data.onset
        else:
            histogram[pitchclass] += 1

    return histogram





