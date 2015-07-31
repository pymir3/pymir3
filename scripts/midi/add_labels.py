#acexml2tab.py
#
# Converts ACE XML files to tabular string texts.

import argparse
import xml.dom.minidom as minidom

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

xmldoc = minidom.parse(args.infile)
dataset_list = xmldoc.getElementsByTagName('data_set')

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
for dataset in dataset_list:
    lineout = ""

    dataset_id = dataset.getElementsByTagName('data_set_id')
    ID = dataset_id[0].childNodes[0].nodeValue.split('/')[-1]
    lineout += ID

    if args.label is not None:
        lineout += separator
        lineout += labeldict[ID]

    features = dataset.getElementsByTagName('feature')
    for feat in features:
        values = feat.getElementsByTagName('v')
        for val in values:
            lineout += separator
            lineout += val.childNodes[0].nodeValue.replace(',', '.')
            if first_line is True:
                title += separator
                title += str(attN)
                attN += 1

    if first_line is True:
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

