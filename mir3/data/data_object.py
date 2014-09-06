import mir3.data.base_object as bo
import mir3.data.metadata as md

class DataObject(bo.BaseObject):
    """Standard base for interface objects.

    Provides some methods to make it easier to develop interface objects.

    Attributes:
        metadata: object of type Metadata with information about the data
                  stored.
        data: any kind of data the derived class wants to use.
    """

    def __init__(self, metadata=None):
        """Initializes metadata to given value and data to None.

        The metadata isn't copied, so any modifications affect both objects.

        Args:
            metadata: Metadata object to associate with this interface. Default:
            None.
        """
        super(DataObject, self).__init__()

        # Defines a valid metadata
        if metadata is not None:
            self.metadata = metadata
        else:
            self.metadata = md.Metadata();

        # Default data
        self.data = None
