import numpy
try:
    import cPickle as pickle
except:
    import pickle
import sys
import zlib

class NumpyMarker:
    """Marker class to identify that some place used to hold a numpy array.
    """
    def __init__(self, val):
        self.id = val;

class BaseObject(object):
    """Base object that stores itself in compressed format.

    The object saves the numpy arrays separated, as they may not be as
    compressable and may be too expensive to try to compress. The rest of the
    object is stored compressed. This should be used in every class, as pickled
    data can be very redundant.

    Saving and loading must be done through the methods save and load. It
    doesn't provide __getstate__ and __setstate__ because hierarchical use of
    this class (one of its members is also a BaseObject) would lead to poor
    performance, as each one would compress only itself.
    """

    def __init__(self):
        # Creates the name safeguard
        self.__classname = self.__class__.__module__+'.'+self.__class__.__name__

    def save(self, handler, compression_level=1, restore_state=False):
        """Saves the compressed object with its arrays separated.

        Removes every array from the objet so that it can be compressed after
        being pickled. The arrays are stored right after the object. A class
        safeguard is stores also, to avoid loading incorrect values.

        If restore_state is False, the object will not restore the arrays. So
        this method may modify the object provided.

        Args:
            handler: file handler where the object will be saved.
            compression_level: level of data compression. Default: 1.
            restore_state: restore the arrays to the correct places after
                           saving. Should be False if the object will be
                           destroyed right after. Default: False.

        Returns:
            self

        Raises:
            IOError: failed to save the object.
        """
        # Extracts the arrays to save them separately
        array_list = []
        BaseObject.__extract_arrays(self, array_list)

        # Stores class name to guarantee safe loading
        pickle.dump(self.__classname, handler, -1)

        # Stores compressed obj
        self_str = pickle.dumps(self, -1)
        self_compressed = zlib.compress(self_str, compression_level)
        pickle.dump(self_compressed, handler, -1)

        # Stores number of arrays
        pickle.dump(len(array_list), handler, -1)

        # Stores arrays
        for array in array_list:
            numpy.save(handler, array)

        # Restore arrays if needed
        if restore_state:
            BaseObject.__place_arrays(self, array_list)

    def load(self, handler):
        """Loads an object in the compressed format.

        The current object is only used to guarantee that the correct type is
        being loaded. It isn't modified. The loaded object is returned.

        Args:
            handler: file handler used to read.

        Returns:
            Loaded object.

        Raises:
            IOError: failed to load the object.
            TypeError: the object stored is different from the one trying to
                       load or the data is of a unknown type.
        """
        try:
            # Loads classname safeguard
            classname = pickle.load(handler)

            # If the loaded name doesn't match the object, we are trying to load
            # the wrong kind
            if classname != self.__classname:
                raise TypeError("Trying to load an object of type '%s' into one"
                                " of type '%s' through file '%s'." %
                                (classname, self.__classname, handler.name))

            # Load stored object
            self_compressed = pickle.load(handler)
            self_str = zlib.decompress(self_compressed)
            new_self = pickle.loads(self_str)

            # Load number of arrays
            n_arrays = pickle.load(handler)

            # Load arrays
            array_list = []
            for i in range(n_arrays):
                array_list.append(numpy.load(handler))

            # Restore arrays
            BaseObject.__place_arrays(new_self, array_list)

            return new_self

        except EOFError:
            sys.exit("EOF error while loading '%s'. Probably the file didn't"
                     " finish writing." % handler.name)

        return self

    @staticmethod
    def __extract_arrays(obj, array_list):
        """Extracts arrays from objects, placing markers in place.

        Only tuples, lists, dictionaries and BaseObject are called recursively.
        This method modifies its arguments.

        Args:
            obj: object from which to extract arrays.
            array_list: array that will store extracted objects.

        Returns:
            obj without arrays.
        """
        if isinstance(obj, BaseObject):
            for k,v in vars(obj).iteritems():
                setattr(obj, k, BaseObject.__extract_arrays(v, array_list))

        elif isinstance(obj, numpy.ndarray):
            array_list.append(obj)
            return NumpyMarker(len(array_list)-1)

        elif isinstance(obj, list) or isinstance(obj, tuple):
            for i in range(len(obj)):
                obj[i] = BaseObject.__extract_arrays(obj[i], array_list)

        elif isinstance(obj, dict):
            for k,v in obj.iteritems():
                obj[k] = BaseObject.__extract_arrays(v, array_list)

        return obj

    @staticmethod
    def __place_arrays(obj, array_list):
        """Places array back into the object, removing markers.

        Only tuples, lists, dictionaries and BaseObject are called recursively.
        This method modifies its arguments.

        Args:
            obj: object with array markers.
            array_list: arrays to place inside obj.

        Returns:
            obj with arrays.
        """
        if isinstance(obj, BaseObject):
            for k,v in vars(obj).iteritems():
                setattr(obj, k, BaseObject.__place_arrays(v, array_list))

        elif isinstance(obj, NumpyMarker):
            return array_list[obj.id]

        elif isinstance(obj, list) or isinstance(obj, tuple):
            for i in range(len(obj)):
                obj[i] = BaseObject.__place_arrays(obj[i], array_list)

        elif isinstance(obj, dict):
            for k,v in obj.iteritems():
                obj[k] = BaseObject.__place_arrays(v, array_list)

        return obj
