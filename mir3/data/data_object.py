import numpy
import pickle
#import StringIO
import sys
import mir3.data.metadata as md
import zlib

class DataObject(object):
    """Standard base for interface objects.

    Provides some methods to make it easier to develop interface objects.

    Attributes:
        metadata: object of type Metadata with information about the data
                  stored.
        data: any kind of data the derived class wants to use.
    """

    def __init__(self, metadata=None):
        """Initializes metadata to given value and data to None.

        Args:
            metadata: Metadata object to associate with this interface.
        """
        if metadata is not None:
            # I don't think we need to copy here
            self.metadata = metadata
        else:
            self.metadata = md.Metadata();
        self.__classname = self.__class__.__module__+'.'+self.__class__.__name__
        self.data = None

#    def __getstate__(self):
#        """Overwrites pickle saving to use class save.
#        """
#        string = StringIO.StringIO()
#        self.save(string)
#        value = string.getvalue()
#        string.close()
#        return value
#
#    def __setstate__(self, state):
#        """Overwrites pickle loading to use class save.
#        """
#        string = StringIO.StringIO(state)
#        self.__init__() # Makes sure self.__classname is available
#        self.load(string)
#        string.close()

    def save(self, handler, save_data=True, metadata_compression=1,
             data_compression=1):
        """Saves the object.

        Saves the class name, to avoid loading the object to a different type.
        Then saves the metadata and, if requested, save the data. Currently we
        save data using numpy if it's a ndarray, using pickle otherwise.

        Args:
            handler: file handler where things will be saved.
            save_data: flag indicating whether we should save the data. Default
                       to True.

        Returns:
            self

        Raises:
            IOError: failed to save the object.
        """
        pickle.dump(self.__classname, handler)

        metadata_string = pickle.dumps(self.metadata)
        metadata_compressed = zlib.compress(metadata_string,
                                            metadata_compression)
        pickle.dump(metadata_compressed, handler)

        if save_data:
            if isinstance(self.data, numpy.ndarray):
                pickle.dump('n', handler)
                numpy.save(handler, self.data)
            else:
                pickle.dump('p', handler)
                #pickle.dump(self.data, handler)
                data_string = pickle.dumps(self.data)
                data_compressed = zlib.compress(data_string, data_compression)
                pickle.dump(data_compressed, handler)

        return self

    def load(self, handler, load_data=True, load_metadata=True):
        """Loads an object.

        This is the symmetric method to save.

        Args:
            handler: file handler used to read.
            load_data: flag indicating whether we should load the data. Default
                       to True.

        Returns:
            self

        Raises:
            IOError: failed to load the object.
            TypeError: the object stored is different from the one trying to
                       load or the data is of a unknown type.
        """

        try:
            classname = pickle.load(handler)
            if (classname != self.__classname):
                raise TypeError("Trying to load an object of type '%s' into one"
                                " of type '%s' through file '%s'" %
                                (classname, self.__classname, handler.name))

            metadata_compressed = pickle.load(handler)
            if load_metadata:
                metadata_string = zlib.decompress(metadata_compressed)
                metadata = pickle.loads(metadata_string)

            if load_data:
                data_type = pickle.load(handler)
                if data_type == 'n':
                    data = numpy.load(handler)
                elif data_type == 'p':
                    #data = pickle.load(handler)
                    data_compressed = pickle.load(handler)
                    data_string = zlib.decompress(data_compressed)
                    data = pickle.loads(data_string)
                else:
                    raise IOError("Unknown data type '%s' inside file '%s'" %
                                  (data_type, handler.name))

        except EOFError:
            sys.exit("EOF error while loading '%s'. Probably the file didn't"
                     " finish writing." % handler.name)

        if load_metadata:
            self.metadata = metadata
        if load_data:
            self.data = data

        return self
