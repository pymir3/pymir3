#acexml2tab.py
#
# Converts ACE XML files to tabular string texts.

import argparse
import xml.dom.minidom as minidom

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('infile', help='input filename')
parser.add_argument('outfile', help='output filename')
parser.add_argument('--csv', default=False, action='store_true',\
                    help='use commas instead of tabs to separate data\
                            (default: False)')
args = parser.parse_args()

#print args.infile
#print args.outfile
#print args.csv

xmldoc = minidom.parse(args.infile)
dataset_list = xmldoc.getElementsByTagName('data_set')

for dataset in dataset_list:
    dataset_id = dataset.getElementsByTagName('data_set_id')
    print dataset_id[0].toxml()
    print dataset_id[0].childNodes[0].nodeValue # YAY !

#print(len(itemlist))
#print(itemlist[0].attributes['name'].value)
#for s in itemlist:
#        print(s.attributes['name'].value)



