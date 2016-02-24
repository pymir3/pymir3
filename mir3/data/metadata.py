import hashlib
import pickle
import StringIO

import mir3.data.blank as blank

class Metadata(blank.Blank):
    """Aggregates all metadata of an interface object.

    During its creation, a dictionary in form of keyword arguments is used to
    define which attributes will be available in the metadata. After
    initialization, we block creation of new attributes as the metadata should
    be fixed.
    """

    def __init__(self, **kw):
        """Initializes the attributes given in keyword arguments.

        No new attribute is allowed after this.

        Args:
            kw: keyword arguments.
        """
        super(Metadata, self).__init__(**kw)

class BlobMetadata(Metadata):
    """Metadata for a blob.

    Saves the name and sha256 of a file in metadata format.

    Metadata available information:
        -name: name of the blob.
        -sha256: blob's sha256.
    """

    def __init__(self, name, blob):
        """Creates metadata using a blob.

        Args:
            name: name of the blob to be stored in metadata.
            blob: values to be hashed to provide checking.
        """
        super(BlobMetadata, self).__init__(
                name=name,
                sha256=hashlib.sha256(blob).hexdigest())

class FileMetadata(BlobMetadata):
    """Metadata for a file.

    Reads the file and provides it as a blob for hashing.
    """

    def __init__(self, handler):
        """Creates metadata using a file handler.

        We only allow file handlers to avoid invalid file names. However, we
        don't check if it really is a file handler, as we use only the name
        associated.

        Args:
            handler: an open file handler.

        Raises:
            IOError: handler provided an invalid name.
        """
        super(FileMetadata, self).__init__(
                name=handler.name,
                blob=open(handler.name, 'rb').read())

class ObjectMetadata(BlobMetadata):
    """Metadata for an object.

    Pickles the object and provides it as a blob for hashing.
    """

    def __init__(self, obj):
        """Creates metadata using an object.

        Uses pickle to get the file blob and uses the class name as the blob
        name.

        Args:
            obj: a pickable object.
        """
        # Dumps object into a blob
        string = StringIO.StringIO()
        pickle.dump(obj, string)
        val = string.getvalue()
        string.close()

        super(ObjectMetadata, self).__init__(
                name=obj.__class__.__name__,
                blob=val)
