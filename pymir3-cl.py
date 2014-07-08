#!/usr/bin/env python

import argparse

import mir3.modules

def get_parser():
    parser = argparse.ArgumentParser(description="""Minion to run PyMIR3's
                                     tasks""")
    mir3.modules.load(parser)
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
