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

# Event lists:
# A list containing all onsets and offsets of a note sequence.
# The list will contain information as:
# time pitch event_type (1 = onset, 0 = offset)
# TODO: If this list gets used very often, then in will be ported to a data
# structure of its own.

def event_list(sequence):
    event_list = []
    for note in sequence:
        new_onset = [note.data.onset, note.data.pitch, 1]
        new_offset = [note.data.offset, note.data.pitch, 0]
        event_list.append(new_onset)
        event_list.append(new_offset)

    sorted_list = sorted(event_list, key=lambda x: x[0])

    return sorted_list

def note_density(eventList, time_resolution=0.005, duration=False):
    """Returns note density (number of simultaneous notes) statistics

    Returns:
    (mean, std, min, max)

    If duration is set to True, then these statistics will be weighted acording
    to their time.

    The time resolution is used to detect chords that are not played exactly at
    the given time.
    """


    density_accumulator = 0
    densities = []
    onsets = 0
    offsets = 0
    time_array = []
    current_time = 0.0
    event_number = 0 # counter
    while event_number < len(eventList):
        event = eventList[event_number]

        if (abs(event[0] - current_time) > time_resolution):
            # Accumulate and proceed to next event
            if duration is True:
                time_array.append(event[0]-current_time)
            else:
                time_array.append(1)
            densities.append(onsets-offsets)
            current_time = event[0]


        if event[2] == 1:
            # Add a new onset
            density_accumulator += 1
            onsets += 1
        else:
            density_accumulator -= 1
            offsets += 1

        event_number += 1

    # Estimate statistics:
    d = numpy.array(densities)
    t = numpy.array(time_array)

    dMean = numpy.mean(d)
    dDev = numpy.std(d)
    dMax = numpy.max(d)
    dMin = numpy.min(d)

    return (dMean, dDev, dMax, dMin)


def interval_histogram(eventList, folded=True,\
        time_resolution=0.005, duration=False):
    """Returns interval histogram

    If folded is True, the resulting histogram will have all intervals folded to
    a 12-tone scale (%12)

    If duration is set to True, then these statistics will be weighted acording
    to their time.

    The time resolution is used to detect chords that are not played exactly at
    the given time.
    """

    note_accumulator = []
    interval_accumulator = []
    onsets = 0
    offsets = 0
    time_array = []
    current_time = 0.0
    event_number = 0 # counter
    while event_number < len(eventList):
        event = eventList[event_number]

        if (abs(event[0] - current_time) > time_resolution):
            # Accumulate and proceed to next event
            if duration is True:
                time_array.append(event[0]-current_time)
            else:
                time_array.append(1)

            for x in xrange(len(note_accumulator)):
                for y in xrange(x):
                    interval_accumulator.append(abs(note_accumulator[x]-\
                            note_accumulator[y]))

            current_time = event[0]


        if event[2] == 1:
            # Add a new onset
            note_accumulator.append(event[1])
            onsets += 1
        else:
            note_accumulator.remove(event[1])
            offsets += 1

        event_number += 1

    if folded is True:
        hist = numpy.zeros(12)
        for i in interval_accumulator:
            hist[i%12] += 1

    hist = hist / numpy.sum(hist)

    return hist






