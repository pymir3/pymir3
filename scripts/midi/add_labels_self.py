#add_labels_self.py
#
# Adds labels as a columns in files

import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('infile', help='input filename')
parser.add_argument('outfile', help='output filename')
parser.add_argument('--label', default=None,\
            help='optional label file (see specification)')
parser.add_argument('--csv', default=False, action='store_true',\
                    help='use commas instead of tabs to separate data\
                            (default: False)')
args = parser.parse_args()

#print args.infile
#print args.outfile
#print args.csv

if args.csv is True:
    separator = ", "
else:
    separator = "\t"

# Open optional label file
if args.label is not None:
    labeldict = {}
    with open(args.label, 'rb') as f:
        for line in f:
            p = line.replace('\n', '').split(' ')
            labeldict[p[0]] = p[1]


fout = open(args.outfile, 'wb')
title = "ID"
if args.label is not None:
    title += separator
    title += "LABEL"

first_line = True
attN = 1
with open(args.infile, 'rb') as f:


    for line in f:
        print line
        p = line.replace('\n', '').split(' ')
        lineout = ""
        ID = p[0].split('/')[-1]
        lineout += ID
        lineout += separator
        lineout += labeldict[ID]
        for i in range(1, len(p)):
            lineout += separator
            lineout += p[i]

        if first_line is True:
            for i in range(1, len(p)):
                title += separator
                title += str(i)
            title += "\n"
            fout.write(title)
            first_line = False

        lineout += "\n"
        fout.write(lineout)

fout.close()

#print(len(itemlist))
#print(itemlist[0].attributes['name'].value)
#for s in itemlist:
#        print(s.attributes['name'].value)


