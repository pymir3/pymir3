# Symbolic feature extraction from sequences of notes
# WARNING: sort your note sequences according to onset time before using these
# functions!

import numpy

def range(sequence):
    """Returns the note rance in a tuplet (min_note, max_note)"""
    if len(sequence) == 0:
        return (0, 0)

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
    if len(sequence) == 0:
        return histogram

    for note in sequence:
        pitchclass = note.data.pitch % 12
        if duration is True:
            histogram[pitchclass] += note.data.offset - note.data.onset
        else:
            histogram[pitchclass] += 1

    histogram /= numpy.sum(histogram)
    return histogram

def tonality(histogram):
    """Calculates tonality of the pitchclass_histogram.

    Returns the estimated tonality (argmax(pitchclass_histogram)) and a
    flipped histogram considering [0] to be the estimated tonic
    """
    tonality = numpy.argmax(histogram)
    new_histogram =\
            numpy.concatenate((histogram[tonality:],histogram[0:tonality]))
    return (tonality, new_histogram)



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
    if len(eventList) == 0:
        return (0, 0, 0, 0)

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


def interval_histogram(eventList, folds=12,\
        time_resolution=0.005, duration=False):
    """Returns interval histogram

    If folded is True, the resulting histogram will have all intervals folded to
    a 12-tone scale (%12)

    If duration is set to True, then these statistics will be weighted acording
    to their time.

    The time resolution is used to detect chords that are not played exactly at
    the given time.
    """
    if len(eventList) == 0:
        return numpy.zeros(folds)


    note_accumulator = []
    interval_accumulator = []
    current_time = 0.0
    event_number = 0 # counter
    while event_number < len(eventList):
        event = eventList[event_number]

        if (abs(event[0] - current_time) > time_resolution):
            # Accumulate and proceed to next event

            for x in xrange(len(note_accumulator)):
                for y in xrange(x):
                    interval_accumulator.append(\
                            [abs(note_accumulator[x] - note_accumulator[y]),\
                            event[0]-current_time])

            current_time = event[0]


        if event[2] == 1:
            # Add a new onset
            note_accumulator.append(event[1])
        else:
            note_accumulator.remove(event[1])


        event_number += 1

    hist = numpy.zeros(folds)
    if duration is True:
        for i in interval_accumulator:
            hist[i[0]%folds] += i[1]
    else:
        for i in interval_accumulator:
            hist[i[0]%folds] += 1.0

    hist = hist / numpy.sum(hist)

    return hist


def relative_range(eventList,
        time_resolution=0.005, duration=False):
    """Returns interval histogram

    If duration is set to True, then these statistics will be weighted acording
    to their time.

    The time resolution is used to detect chords that are not played exactly at
    the given time.
    """
    if len(eventList) == 0:
        return (0, 0, 0)

    time_accumulator = []
    range_accumulator = []
    note_accumulator = []
    current_time = 0.0
    event_number = 0 # counter
    while event_number < len(eventList):
        event = eventList[event_number]

        if (abs(event[0] - current_time) > time_resolution):
            # Accumulate and proceed to next event
            if len(note_accumulator) > 0:
                range_accumulator.append(max(note_accumulator) -\
                    min(note_accumulator))
                time_accumulator.append(event[0]-current_time)

            current_time = event[0]

        if event[2] == 1:
            # Add a new onset
            note_accumulator.append(event[1])
        else:
            note_accumulator.remove(event[1])

        event_number += 1

    range_array = numpy.array(range_accumulator)
    if duration is True:
        time_array = numpy.array(time_accumulator)
        maxRange = numpy.max(range_array)
        meanRange = numpy.sum(range_array * time_array) /\
                numpy.sum(time_array)
        devRange = numpy.sum(time_accumulator * ((range_array-meanRange)**2))/\
                numpy.sum(time_array)
    else:
        maxRange = numpy.max(range_array)
        meanRange = numpy.mean(range_array)
        devRange = numpy.std(range_array)

    return (maxRange, meanRange, devRange)


def rhythm_histogram(eventList, rhythm_bins=24,\
        time_resolution=0.005):
    """Estimates rhythm histogram, given an event list

    The time resolution is used to detect chords that are not played exactly at
    the given time.
    """

    current_time = 0.0
    event_number = 0 # counter
    ioi_list = []
    last_ioi = None

    while event_number < len(eventList):
        event = eventList[event_number]

        if (abs(event[0] - current_time) > time_resolution) and\
                    (event[2] == 1):
            this_ioi = float(event[0] - current_time)

            if last_ioi is not None:
                ioi_list.append(this_ioi / last_ioi)

            last_ioi = this_ioi
            current_time = event[0]

        event_number += 1

    ioi_list = numpy.array(ioi_list)
    ioi_list = numpy.log2(ioi_list)

    rhythm_histogram = numpy.histogram(ioi_list, bins=rhythm_bins,\
            range=(-6, 6), density=True)

    return rhythm_histogram





