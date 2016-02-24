import mir3.data.base_object as bo

class Blank(bo.BaseObject):
    """Class with arbitrary but fixed attributes.

    During its creation, a dictionary in form of keyword arguments is used to
    define which attributes will be available. After initialization, we block
    creation of new attributes.

    The idea is to ease the use of arbitrary descriptors similar to
    dictionaries, but with simpler access as the keys must be strings.

    Example:
    b = Blank(attr1 = 'val1')
    print b.attr1    # prints 'val1'
    print b.attr2    # error
    b.attr2 = 'val2' # error
    """

    # Control weather the attributes are frozen
    __isfrozen = False

    def __init__(self, **kw):
        """Initializes the attributes given in keyword arguments.

        No new attribute is allowed after this.
        """
        super(Blank, self).__init__()

        # Keeps the keywords in case someone tries to set an invalid one
        self.__keywords = sorted(kw.keys())

        # Sets the given values
        for k,v in kw.iteritems():
            setattr(self, k, v)

        # Freezes attributes creation
        self.__isfrozen = True

    def __setattr__(self, name, value):
        """Sets an attribute.

        If the attribute name was given during initialization, it's set to
        value. Raises an error otherwise.

        Args:
            name: requested attribute name.
            value: value to store.

        Raises:
            AttributeError: Attribute name was invalid. Provides a list of valid
                            ones.
        """
        # If the object is frozen and we are trying to set an invalid attribute,
        # raises an error
        if self.__isfrozen and not hasattr(self, name):
            raise AttributeError("Trying to set invalid attribute '%s'. Valid "
                                 "attributes are: %s." %
                                 (name, ", ".join(self.__keywords)))

        # Otherwise, set the attribute
        object.__setattr__(self, name, value)

    def get(self, attr):
        """Gets an attribute's value based on addressing.

        The argument is given by "attr1.attr2.attr3", where attr_1 is a valid
        attribute name somewhere in the hierarchy tree, and attr_n has a child
        named attr_n+1. If the attribute isn't found, raises an error.

        Example:
        obj = Blank(attr1 = Blank(attr2 = 0))
        print obj.get('attr1.attr2') # prints 0
        print obj.get('invalid_attr') # raises error

        Args:
            attr: attribute address.

        Returns:
            Attribute value.

        Raises:
            ValueError: couldn't find the attribute.
        """
        val, valid = Blank.__get(self, attr.split('.'))

        if not valid:
            raise ValueError("Couldn't find value for '%s'." % attr)

        return val

    @staticmethod
    def __get(obj, attrs):
        """Internal method to implement attribute getting.

        Based on a list of attributes names, find the correct attribute value
        and returns. The object can be:
            - a Blank object, where the attributes are searched
            - a list, where each element is searched
            - a dictionary, where each value is searched
        Other types aren't searched.

        Args:
            obj: object where the attributes are being searched.
            attrs: list of attributes' names.

        Returns:
            Tuple of (value, valid), indicating the attribute's value and
            whether it was found.
        """
        # If the list is empty, got the value
        if attrs == []: return obj, True

        if isinstance(obj, list):
            for e in obj:
                val, valid = Blank.__get(e, attrs)
                if valid: return val, valid

        elif isinstance(obj, dict):
            for e in obj.values():
                val, valid = Blank.__get(e, attrs)
                if valid: return val, valid

        elif isinstance(obj, Blank):
            # If the first attribute is present, dig further
            if hasattr(obj, attrs[0]):
                attr = getattr(obj, attrs[0])
                val, valid = Blank.__get(attr, attrs[1:])
                if valid: return val, valid

            # Otherwise, search each attribute
            for d in dir(obj):
                val, valid = Blank.__get(getattr(obj, d), attrs)
                if valid: return val, valid

        return None, False
