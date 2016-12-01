import mir3.data.blank as blank
import mir3.data.data_object as do
import mir3.data.metadata as md

class LinearDecomposition(do.DataObject):
    """Linear decompositions of matrices.

    This class can hold linear decompositions of many different matrices. It was
    developed so that an operation that creates both sides can work with those
    that create only one.

    Each side's data and metadata are dictionaries. The keys are used to match
    the different sides when both have information on them.

    Metadata available:
        - left: left metadata. Default: {}.
        - right: right metadata. Default: {}.

    Data available:
        - left: left data. Default: {}.
        - right: right data. Default: {}.
    """

    def __init__(self):
        super(LinearDecomposition, self).__init__(
                md.Metadata(input_metadata=None,
                            left={},
                            right={}))

        self.data = blank.Blank(left={},
                                right={})

    def add(self, key, left=None, left_metadata=None, right=None,
            right_metadata=None, replace_key=False):
        """Adds elements to the decomposition.

        Both sides can be used with the same key, but data and metadata for the
        same side must be provided. If the data or metadata isn't provided,
        neither is added to avoid inconsistencies.

        The value None is used to detect if any data wasn't provided, so it
        isn't a valid value to store.

        Args:
            key: key used for the dictionary.
            left: data for the left side.
            left_metadata: metadata for the left side.
            right: data for the right side.
            right_metadata: metadata for the right side.
            replace_key: if the key is already being used, replace the values.

        Returns:
            self

        Raises:
            ValueError: the key provided has already been used in the desired
                        side and replace_key == False.
        """
        # Only insert if data and metadata aren't None
        if left is not None and left_metadata is not None:
            # If the key already exists and we don't want to replace, it's an
            # error.
            if not replace_key and key in self.metadata.left:
                raise ValueError("Key '%r' already present in metadata.left." %
                                 (key,))
            if not replace_key and key in self.data.left:
                raise ValueError("Key '%r' already present in data.left." %
                                 (key,))
            self.metadata.left[key] = left_metadata
            self.data.left[key] = left

        # Samething for the right side
        if right is not None and right_metadata is not None:
            if not replace_key and key in self.metadata.right:
                raise ValueError("Key '%r' already present in metadata.right." %
                                 (key,))
            if not replace_key and key in self.data.right:
                raise ValueError("Key '%r' already present in data.right." %
                                 (key,))
            self.metadata.right[key] = right_metadata
            self.data.right[key] = right

        return self

    def left(self):
        """Generator for left side.

        For each key in the left side, returns it with the associated data and
        metadata.

        Returns:
            Tuple of (key, data, metadata).
        """
        # Create keys
        keys = list(set(self.data.left.keys() + self.metadata.left.keys()))

        # Iterate for the generator
        for k in sorted(keys):
            yield k, self.data.left[k], self.metadata.left[k]

    def right(self):
        """Generator for right side.

        For each key in the right side, returns it with the associated data and
        metadata.

        Returns:
            Tuple of (key, data, metadata).
        """
        # Create keys
        keys = list(set(self.data.right.keys() + self.metadata.right.keys()))

        # Iterate for the generator
        for k in sorted(keys):
            yield k, self.data.right[k], self.metadata.right[k]
