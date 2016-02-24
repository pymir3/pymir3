from MidiOutFile import MidiOutFile

from MidiOutStream import MidiOutStream
from MidiInFile	 import MidiInFile

class NoteOnPrinter(MidiOutStream):
    ppm=96
    spp=60000000/120

    currTime=0

    notes = [0]*90

    def header(self, a, b, division=96):
        self.ppm=division
        print "Found a header!"

    def update_time(self, ticks, wtf):
        self.currTime +=  ticks*self.spp

    def tempo(self, usq=0):
        self.spp = (usq / self.ppm)* (10**(-6))
        print "Changed tempo so there are ", self.spp, " seconds per pulse"

    def note_on(self, channel=0, note=0, velocity=0):
        if channel == 0:
            print channel, note, velocity, self.abs_time(), self.currTime
            self.notes[note]=self.currTime*1.0

    def note_off(self, channel=0, note=0, velocity=0):
        if channel == 0:
            print "Off with note ", note, " with duration ", self.currTime-self.notes[note]
            self.notes[note]=0

event_handler = NoteOnPrinter()
in_file = 'test.mid'



out_file = 'test.mid'
midi = MidiOutFile(out_file)

# non optional midi framework
midi.header(division=96)
midi.start_of_track()
# musical events
midi.tempo(60000000/60)
midi.update_time(0)
midi.note_on(channel=0, note=69)
midi.update_time(96)
midi.note_on(channel=0, note=73)
midi.update_time(96)
midi.note_off(channel=0, note=69)
midi.update_time(96)
midi.note_off(channel=0, note=73)

# non optional midi framework
midi.update_time(0)
midi.end_of_track() # not optional!

midi.eof()


midi_in = MidiInFile(event_handler, in_file)
midi_in.read()


