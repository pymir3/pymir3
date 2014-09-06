import importlib
import inspect
import os

class Subparser(object):
    """Magic class to make command line modules easy.

    The class scans the directory for the module given and finds submodules
    available. For each submodule, process it so that it can be called from the
    command line.
    """

    def __init__(self, parser, dirname, module_name):
        """Do all the magic for this class.

        Scans the directory for the module given and finds submodules available.
        For each submodule, process it so that it can be called from the command
        line.

        Both dirname and module_name are provided so that a wrapper library that
        shadows part of the modules can be used.

        "dirname" should be the directory path for the __init__.py associated
        with module_name

        Args:
            parser: an argparse parser.
            dirname: directory path of the file for the current module.
            module_name: name of the current module.

        Raises:
            ImportError: a module couldn't be imported correctly. This also
                         occurs if a leaf module doesn't provide the
                         get_arguments method inside a class.
        """
        # Looks for file in the directory
        files = os.listdir(dirname)

        # Considers anything ending with "_submodule.py" as a submodule. Sets
        # submodule's name as anything before the "_submodule.py".
        submodules = [f[:-len('_submodule.py')]
                      for f in files if f.split('_')[-1] == 'submodule.py']

        # Everything that isn't a submodule or __init__ and is a python file
        # must be a leaf module (directly callable).
        leaf_modules = [f[:-len('.py')]
                        for f in files if f.split('.')[-1] == 'py' and
                                          f != '__init__.py' and
                                          f.split('_')[-1] != 'submodule.py']

        # Creates subparsers for the current submodule
        subparsers = parser.add_subparsers(help='')

        # Join both kind of modules so they look pretty when sorted, but deals
        # with each one diferently
        for submodule_name in sorted(leaf_modules+submodules):
            if submodule_name in leaf_modules:
                # Imports the leaf module
                submodule = \
                        importlib.import_module(module_name+'.'+submodule_name)

                # Gets the help and associated parser for submodule
                new_parser = Subparser.__get_submodule_parser(submodule,
                        submodule_name, subparsers)

                # As this is a leaf module, it can provide argument list
                class_obj, method_obj = \
                        Subparser.__get_method(submodule, 'get_arguments')

                # If found method, module provides arguments list
                if method_obj is not None:
                    method_obj(class_obj(), new_parser)
                else:
                    print "No class with method 'get_arguments' found while " \
                          "importing %s. Assuming no argument is required." % \
                          module.__name__

            else: # submodule
                # Imports the submodule
                submodule = importlib.import_module(module_name+'.'+\
                        submodule_name+'_submodule')

                new_parser = Subparser.__get_submodule_parser(submodule,
                        submodule_name, subparsers)

                # Recursive call for hierarchy
                Subparser(new_parser, dirname+'/'+submodule_name,
                        module_name+'.'+submodule_name)

    @staticmethod
    def __get_submodule_parser(submodule, submodule_name, subparsers):
        """Gets help and parser for submodule.

        Provides the connection between the module and its submodule. If a help
        message is provided in the submodule, it's used in the description of
        how to the to the submodule. Otherwise, a empty string is used.

        The returned parser should be used to specify the parameters of the
        submodule.

        Args:
            submodule: already imported submodule file.
            submodule_name: name of the submodule to show in the help.
            subparsers: parser for the parent module.

        Returns:
            New parser for the submodule.
        """
        # Gets the command line help, if available.
        m_help = ''
        class_obj, method_obj = Subparser.__get_method(submodule,
                'get_help')

        # If found method, module provides a help
        if method_obj is not None:
            m_help = method_obj(class_obj())
        else:
            print "No class with method 'get_help' found while " \
                  "importing %s. Assuming no help is provided." % \
                  submodule.__name__

        # Adds the module with a help message
        new_parser = subparsers.add_parser(submodule_name, help=m_help)

        return new_parser

    @staticmethod
    def __get_method(module, method_name):
        """Finds a method inside a module.

        Given a module, check if any class inside the module has the method
        desired.

        Args:
            module: module object.
            method_name: name of the desired method.

        Returns:
            Tuple (class object, method object) if found. Tuple (None, None)
            otherwise.
        """
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                for name2, obj2 in inspect.getmembers(obj):
                    if name2 == method_name:
                        return obj, obj2

        return None, None
