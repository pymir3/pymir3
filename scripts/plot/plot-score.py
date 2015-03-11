#!/usr/bin/env python

import argparse
import os

import mir3.data.note as note
import mir3.data.score as score

from svglib import *

whiteNotes = [11, 9, 7, 5, 4, 2, 0] # This is a list of notes that should be white
noteLabels = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def make_lanes(canvas, roll_width, offset, space_per_note, minNote, maxNote, space_per_second, minT, maxT):
    # This function will put lanes in the canvas using rectangles
    rec_width = ((maxT-minT)*space_per_second)

    note=maxNote
    initY = offset
    while note>=minNote:

        if (note%12) in whiteNotes:
            color_rect = (255,255,255)
        else:
            color_rect = (200,200,200)

        canvas.add(Rectangle((roll_width,initY),space_per_note,rec_width,color_rect))
        note=note-1
        initY=initY+space_per_note

    return canvas

def make_time_divisions(canvas, roll_width, offset, fontsize, legendY, minT, maxT, space_per_second, division_time=1.0):
    # This function will put time divisions in the canvas using lines
    currX = roll_width
    deltaX = space_per_second*division_time
    currT = minT
    while currT <= maxT:
        canvas.add(Line((currX,offset), (currX, legendY-fontsize), 1))
        canvas.add(Text( (currX,legendY), str(currT), fontsize, (0,0,0) ))
        currT = currT+division_time
        currX = currX+deltaX

    canvas.add(Text( (roll_width/2, legendY), "t (s)", fontsize, (0,0,0)))
    return canvas


def make_keyboard(canvas, roll_width, offset, fontsize, space_per_note, minNote, maxNote):
    # This function will put a keyboard in the given canvas using the given parameters.
    note=maxNote
    initY = offset
    while note>=minNote:

        if (note%12) in whiteNotes:
            color_rect = (255,255,255)
            color_text = (0,0,0)
        else:
            color_rect = (0,0,0)
            color_text = (255,255,255)

        canvas.add(Rectangle((0,initY),space_per_note,roll_width,color_rect))
        canvas.add(Text((roll_width/2, initY+(space_per_note)*0.7), noteLabels[note%12]+str((note/12)-1), fontsize, color_text))
        note=note-1
        initY=initY+space_per_note

        #canvas.add(Line((roll_width,offset), (roll_width, initY), 5))
    return canvas

def add_note(canvas, note, roll_width, CanvasOffset, space_per_note, space_per_second, maxNote, minT, color, height_ratio):
    # This functions adds a note to the given canvas. The note should be specified as [onset, offset, pitch]
    onset = note[0]
    offset = note[1]
    pitch = note[2]
    noteY = CanvasOffset + (maxNote-pitch)*space_per_note+ 0.5*(1-height_ratio)*space_per_note
    noteX0 = roll_width + (onset-minT)*space_per_second
    noteX1 = (offset-onset)*space_per_second


    canvas.add(Rectangle( (noteX0, noteY), space_per_note*height_ratio, noteX1, color) )
    return canvas

def plotList(score_file, width=400, height=300, roll_width=30, tLimits=None, nLimits=None, fontsize=12,  color=(100,100,100), thickness=0.5, previousState=None):
    # This functions returns a Scene (see the svglib) that is a representation for the transcription. The parameters are:
    # width, height: the total width and height of the plot
    # roll_width: the width of the reference roll on the left. If you use 0, then you will see no reference keyboard
    # (it is very recommended that you don't do it, because, the keyboard is really cute!)
    # tLimits, nLimits: lists with two elements [a, b] specifying the limits within the piano roll will be plotted. If none is specified, uses the whole transcription
    # fontsize: the size of the font that will be used in the text
    # color, opacity: parameters that tells the color of the boxes that will be shown

    s = score.Score().load(score_file)
    if nLimits == None:
        minNote = s.data[0].data.pitch
        maxNote = s.data[0].data.pitch
        for n in s.data:
            if n.data.pitch < minNote:
                minNote = n.data.pitch
            if n.data.pitch > maxNote:
                maxNote = n.data.pitch
        minNote = minNote - 1
        maxNote = maxNote + 1
    else:
        minNote = int(nLimits[0])
        maxNote = int(nLimits[1])

    if tLimits==None:
       minT, maxT = s.get_timespan()
    else:
        minT = tLimits[0]
        maxT = tLimits[1]

    if maxT==minT:
        maxT=minT+1

    space_for_axis = fontsize*2
    space_per_note = (height-space_for_axis)/(maxNote-minNote+1)
    space_per_second = (width-roll_width)/(maxT-minT)
    legendY = height-fontsize

    print space_per_note
    if previousState==None:
        canvas = Scene('svg',height,width)
        canvas = make_keyboard(canvas, roll_width, 0, fontsize, space_per_note, minNote, maxNote)
        canvas = make_time_divisions(canvas, roll_width, 0, fontsize, legendY, minT, maxT, space_per_second, 0.5)
        canvas = make_lanes(canvas, roll_width, 0, space_per_note, minNote, maxNote, space_per_second, minT, maxT)
    else:
        canvas = previousState

    for note in s.data:
        newnote = [note.data.onset, note.data.offset, int(note.data.pitch)]
        canvas = add_note(canvas, newnote, roll_width, 0, space_per_note, space_per_second, maxNote, minT, color, thickness)

    return canvas

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot a spectrogram')
    parser.add_argument('infile', type=argparse.FileType('rb'),\
help="""Input spectrogram file""")
    parser.add_argument('outfile', \
help="""Output figure file""")
    parser.add_argument('--width', type=int, default=300, help="""Output width\
            (inches).\
            Default: 3.45 (one column)""")
    parser.add_argument('--height', type=int, default=200, help="""Output\
            height (inches).\
            Default: 2.0""")
    args = parser.parse_args()
    svg_canvas = plotList(args.infile, width=args.width, height=args.height)
    svg_canvas.write_svg(args.outfile)


