class Module(object):
    """Base class for all modules.

    This class provides the methods needed for the modules to load correctly and
    be used from the command line, if possible.
    """

    def get_help(self):
        """Provides a default empty help message.

        Returns:
            Empty string.
        """
        return ''

    def get_arguments(self, parser):
        """Get the arguments for the module.

        Calls build_arguments and setups the parser run. This method should only
        be caleed if the module was called from the command line.

        Args:
            parser: an argparse parser.
        """
        self.build_arguments(parser)

        # Default run for the parser is to call the run method for the class
        parser.set_defaults(run = lambda args: self.__class__().run(args))

    def build_arguments(self, parser):
        """Builds the argument list for the module.

        The default implementation does nothing. This method should only
        be called if the module was called from the command line.

        Args:
            parser: an argparse parser.
        """
        pass

    def run(self, args):
        """Runs the module from command line.

        This method should be implemented in the children classes.

        Raises:
            NotImplementedError: error exposing which class was called from the
                                 command line and didn't implement this.
        """
        raise NotImplementedError("Method 'run' not implemented for '%s'. It "
                                  "can't be called from the command line." %
                                  self.__class__.__name__)
