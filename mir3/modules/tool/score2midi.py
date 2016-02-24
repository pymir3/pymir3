import argparse
import mir3.data.note as note
import mir3.data.score as score
import mir3.lib.midi.MidiOutFile as MidiOutFile
import mir3.module

class Score2Midi(mir3.module.Module):
    def get_help(self):
        return """convert the internal score representation to midi"""

    def build_arguments(self, parser):
        parser.add_argument('infile', type=argparse.FileType('r'), help="""score
                            file""")
        parser.add_argument('outfile', type=argparse.FileType('w'), help="""midi
                            file""")

    def run(self, args):
        s = score.Score().load(args.infile)

        with MidiWriter(args.outfile) as mw:
            for n in s.data:
                mw.add_note(n)

class MidiWriter:
    """Helper to write MIDI files.

    Uses the external midi library to create midi files from a score. The events
    are added to a dictionary, because MIDI requires things to be written in
    order, so we can't add them instantly. Not every feature available in the
    MIDI format is available here yet.

    The class provides safeguards to save the events to the MIDI file on object
    destruction. It can also be used with the 'with' statement.

    Any events are destructed when a new file is opened.

    Attributes:
        division: number of divisions.
        events: dictionary of events, where the keys are timestamps and values
                are list of events.
        midi: midi file used to write. The value is None if no file is open.
    """

    def __init__(self, file_handle, division=96, bmp=60):
        """Starts a new MIDI file.

        Creates the file and write header and starting BMP.

        Args:
            file_handle: handle for the file to be written.
            divisions: number of divisions. Default: 96.
            bmp: beats per minute at the start. Default: 60.
        """
        self.midi = MidiOutFile.MidiOutFile(file_handle)
        self.division = division
        self.midi.header(division = division)
        self.midi.start_of_track()
        self.events = {}
        self.set_BMP(bmp)

    def add_event_at(self, time, event):
        """Adds an event to a certain time.

        If no event exists on the time, starts the list. The event is stored at
        the list's end.

        Args:
            time: timestamp for the event.
            event: event description.

        Returns:
            self
        """
        if time not in self.events:
            self.events[time] = []
        self.events[time].append(event)

        return self

    def add_note(self, note, channel=0):
        """Adds a Note object to a channel.

        Uses the note onset and offset to compute the time.

        Args:
            note: Note object.
            channel: channel to store the note. Default: 0.

        Returns:
            self
        """
        if note is None:
            raise ValueError, 'Invalid note.'

        onset = int(note.data.onset * self.division)
        onset_event = {'name': 'onset', 'pitch': note.data.pitch,
                       'channel': channel}
        self.add_event_at(onset, onset_event)

        offset = int(note.data.offset * self.division)
        offset_event = {'name': 'offset', 'pitch': note.data.pitch,
                        'channel': channel}
        self.add_event_at(offset, offset_event)

        return self

    def set_BMP(self, bmp, time=0):
        """Sets the BMP at a certain time.

        Args:
            bmp: beats per minute values.
            time: timestamp.

        Returns:
            self
        """
        time = int(time * self.division)
        event = {'name': 'tempo', 'value': 60000000/int(bmp)}
        self.add_event_at(time, event)

        return self

    def write_events(self):
        """Writes the events stored and close the file.

        If there's no file, nothing is done. The events dictionary is cleaned
        upon completion.

        Returns:
            self
        """
        if self.midi is not None:
            time_scale = 1
            last_time = None
            for time in sorted(self.events):
                if last_time is None:
                    self.midi.update_time(int(time), relative = False)
                else:
                    self.midi.update_time(int((time-last_time)*time_scale),
                                          relative = True)
                last_time = time

                for event in self.events[time]:
                    if event['name'] == 'tempo':
                        self.midi.tempo(event['value'])
                        time_scale = 1/(event['value']*1e-6)
                    elif event['name'] == 'onset':
                        self.midi.note_on(channel = event['channel'],
                                          note = event['pitch'])
                    elif event['name'] == 'offset':
                        self.midi.note_off(channel = event['channel'],
                                           note = event['pitch'])
                    else:
                        raise ValueError, 'Unknown MIDI event.'

            self.events = {}
            self.close()

    def close(self):
        """Closes the file and add tail data.

        If the file is open, writes the things that the file format requires at
        the end.

        Returns:
            self
        """
        if self.midi is not None:
            self.midi.update_time(0)
            self.midi.end_of_track()
            self.midi.eof()
            self.midi = None

        return self

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.write_events()

    def __del__(self):
        self.write_events()
