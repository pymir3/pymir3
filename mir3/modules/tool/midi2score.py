import argparse
import mir3.data.metadata as md
import mir3.data.note as note
import mir3.data.score as score
import mir3.lib.midi.MidiOutStream as MidiOutStream
import mir3.lib.midi.MidiInFile as MidiInFile
import mir3.module

class Midi2Score(mir3.module.Module):
    def get_help(self):
        return """convert a midi to the internal score representation"""

    def build_arguments(self, parser):
        parser.add_argument('-i','--instrument', help="""instrument associated
                            with the labels file provided""")

        parser.add_argument('channel', type=int, help="""midi file""")
        parser.add_argument('infile', type=argparse.FileType('r'), help="""midi
                            file""")
        parser.add_argument('outfile', type=argparse.FileType('w'),
                            help="""score file""")

    def run(self, args):
        with MidiReader(args.infile) as mr:
            mr.scores[args.channel].metadata.instrument = args.instrument
            mr.scores[args.channel].save(args.outfile)

class MidiReader(MidiOutStream.MidiOutStream):
    """Reads a MIDI file and create the scores.

    For each channel in the MIDI, creates a Score object containing the Notes
    for that channel.

    Attributes:
        channels: dictionary of channels registering notes onsets and offsets.
        current_time: timestamp for events.
        division: number of divisions. Default: 96.
        file_handle: file handle provided in constructor.
        ssp: timing scale, related to BPM.
    """

    def __init__(self, file_handle):
        """Initializes and reads the MIDI file.

        Args:
            file_handle: handle for an open MIDI file.
        """
        self.channels = {}
        self.division = 96
        self.ssp = 60000000/120
        self.current_time = 0
        self.file_handle = file_handle

        midi_in = MidiInFile.MidiInFile(self, file_handle)
        midi_in.read()

    def create_channel(self, channel):
        if channel not in self.channels:
            self.channels[channel] = {}

    def create_note_on_channel(self, channel, note):
        self.create_channel(channel)
        if note not in self.channels[channel]:
            self.channels[channel][note] = {'onset': [], 'offset': []}

    def header(self, a, b, division=96):
        self.division = division

    def update_time(self, ticks=0, relative=True):
        if relative:
            self.current_time += ticks*self.ssp
        else:
            self.current_time = ticks*self.ssp

    def tempo(self, usq=0):
        self.ssp = (usq/self.division) * (10**(-6))

    def note_on(self, channel=0, note=0x40, velocity=0x40):
        self.create_note_on_channel(channel, note)
        self.channels[channel][note]['onset'].append(self.current_time)

    def note_off(self, channel=0, note=0x40, velocity=0x40):
        self.create_note_on_channel(channel, note)
        self.channels[channel][note]['offset'].append(self.current_time)

    def eof(self):
        self.scores = {}
        for channel in self.channels.keys():
            s = score.Score()
            for n in self.channels[channel].keys():
                onsets = self.channels[channel][n]['onset']
                offsets = self.channels[channel][n]['offset']
                onsets.sort()
                offsets.sort()

                if len(onsets) != len(offsets):
                    raise IOError, \
                        """Got different number of onsets and offsets for the
                        same note."""

                wrong_durations = [(off-on) < 0
                                   for on,off in zip(onsets,offsets)]
                if any(wrong_durations):
                    raise IOError, 'Got negative note durations.'

                s.append([note.Note(pitch=n, onset=on, offset=off)
                          for on,off in zip(onsets,offsets)])

            s.metadata.method_metadata = md.Metadata(type="midi")
            s.metadata.input = md.FileMetadata(self.file_handle)

            self.scores[channel] = s

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass
