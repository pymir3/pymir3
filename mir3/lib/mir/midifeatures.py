# Symbolic feature extraction from sequences of notes
# WARNING: sort your note sequences according to onset time before using these
# functions!

import numpy

def range(sequence):
    """Returns the note rance in a tuplet (min_note, max_note)"""
    min_pitch = 999
    max_pitch = 0
    for note in sequence:
        if note.pitch < min_pitch:
            min_pitch = note.pitch
        if note.pitch > max_pitch:
            max_pitch = note.pitch

    return (min_pitch, max_pitch)

def note_histogram(sequence, min_pitch=20, max_pitch=108):
    """Returns a note histogram of the sequence"""
    histogram = numpy.zeros((1, max_pitch-min_pitch))
    for note in sequence:
        histogram[note.pitch-min_pitch] += 1

    return histogram


