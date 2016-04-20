#!/usr/bin/env python

import argparse
import os.path

import mir3.subparser

def get_parser():
    parser = argparse.ArgumentParser(description="""Minion to run PyMIR3's
                                     tasks""")

    dirname = os.path.dirname(mir3.subparser.__file__)+'/modules'
    module_name = 'mir3.modules'
    mir3.subparser.Subparser(parser, dirname, module_name)
    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    if vars(args) == {}: # no args
        parser.print_help()
    else:
        args.run(args)

if __name__ == '__main__':
    main()
