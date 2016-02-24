import argparse
import numpy
import pickle
import sys
import zlib

import mir3.data.blank as blank
import mir3.module

class Any(mir3.module.Module):
    """Displays any DataObject.

    This is a major hack inside the data structure and should be treated
    carefully.
    """

    def get_help(self):
        return """display any DataObject stored"""

    def build_arguments(self, parser):
        parser.add_argument('-l','--level', type=int, default=-1, help="""number
                            of levels to print from the metadata""")
        parser.add_argument('-s','--spacing', type=int, default=2,
                            help="""number of spaces to indent (default:
                            %(default)s""")
        parser.add_argument('-m','--metadata', action='store_true',
                            default=False, help="""show the metadata""")
        parser.add_argument('-d','--data', action='store_true', default=False,
                            help="""show the data""")

        parser.add_argument('infile', type=argparse.FileType('rb'),
                            help="""object file""")

    def run(self, args):
        if args.spacing < 0:
            print "Wrong number for spacing: %d" % args.spacing
            sys.exit(1)

        # Gets the name of the class stored in the file
        classname = pickle.load(args.infile)
        print 'Stored class name:',classname

        # As the object load expects that the classname is still stored (used to
        # prevent wrong loads), resets the file
        args.infile.seek(0)

        # Creates an instace using the read class name
        obj = eval('%s()' % classname).load(args.infile)

        spacing = ' '*args.spacing

        if args.metadata:
            print ''
            print 'Metadata:'
            self.print_obj(obj.metadata, args.level, spacing, spacing)

        if args.data:
            print ''
            print 'Data:'
            self.print_obj(obj.data, args.level, spacing, spacing)

    def print_obj(self, obj, level, prefix='', spacing=''):
        """Prints the object in a hierarchical way.

        Each level gets an indentation given by the prefix.

        Args:
            obj: object to be printed.
            level: desired level to print. It is decremented until 0.
            prefix: identation prefix used.
            spacing: space to add at each recursive level.
        """
        # Prints a summary of what is store on this level
        if level == 0:
            if isinstance(obj, blank.Blank):
                print prefix+obj.__class__.__module__+'.'+\
                        obj.__class__.__name__+' object'
            elif isinstance(obj, numpy.ndarray):
                print prefix+'numpy array %r' % (obj.shape,)
            elif isinstance(obj, list):
                print prefix+'list with %d element%s' %\
                (len(obj), '' if len(obj) == 1 else 's')
            elif isinstance(obj, tuple):
                print prefix+'tuple with %d element%s' %\
                (len(obj), '' if len(obj) == 1 else 's')
            elif isinstance(obj, dict):
                print prefix+'dictionary with %d element%s' %\
                (len(obj), '' if len(obj) == 1 else 's')
            elif isinstance(obj, str):
                print prefix+obj
            else:
                print '%s%r' % (prefix, obj)
            return

        # For each case, defines the appropriate way to show the structure
        if isinstance(obj, blank.Blank):
            attrs = obj._Blank__keywords
            for a in attrs:
                print prefix+a
                self.print_obj(getattr(obj,a), level-1, prefix+spacing, spacing)
        elif isinstance(obj, numpy.ndarray):
            print prefix+'numpy array %r' % (obj.shape,)
        elif isinstance(obj, list):
            for i in range(len(obj)):
                print prefix+'list[%d]' % i
                self.print_obj(obj[i], level-1, prefi+spacing, spacing)
        elif isinstance(obj, tuple):
            for i in range(len(obj)):
                print prefix+'tuple[%d]' % i
                self.print_obj(obj[i], level-1, prefix+spacing, spacing)
        elif isinstance(obj, dict):
            for key in sorted(obj.keys()):
                print prefix+'dict[%r]' % (key,)
                self.print_obj(obj[key], level-1, prefix+spacing, spacing)
        elif isinstance(obj, str):
            print prefix+obj
        else:
            print '%s%r' % (prefix, obj)
