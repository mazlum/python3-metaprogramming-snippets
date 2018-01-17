# A New Metaclass with OrderedDict
from collections import OrderedDict
from signature import (
    Descriptor,
    make_signature,
    PositiveInteger,
    String,
    Float
)


# Duplicate Definitions
# If inclined, you could do even better
# Make a new kind of dict
class NoDuplicateOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if key in self:
            raise NameError('%s already defined' % key)
        super().__setitem__(key, value)


class StructMeta(type):
    @classmethod
    def __prepare__(metacls, name, bases):
        """
        It creates and returns dictionary to use for execution of the class
        body.

        An OrderedDict will preserve the definition order
        :param name:
        :param bases:
        :return:
        """
        return NoDuplicateOrderedDict()

    def __new__(cls, name, bases, clsdict):
        # Collect Descriptors and set their names
        fields = [
            key for key, val in clsdict.items()
            if isinstance(val, Descriptor)
        ]
        for name in fields:
            clsdict[name].name = name

        # Make the class and signature exactly as before
        clsobj = super().__new__(cls, name, bases, dict(clsdict))

        sig = make_signature(fields)
        setattr(clsobj, '__signature__', sig)
        return clsobj


class Structure(metaclass=StructMeta):
    _fields = []

    def __init__(self, *args, **kwargs):
        bound = self.__signature__.bind(*args, **kwargs)
        for name, val in bound.arguments.items():
            setattr(self, name, val)


class Stock(Structure):
    # We don't have to use __field anymore.
    # _fields = ['name', 'shares', 'price']
    # And we don't have to use name
    # name = String('name')
    # It's just like Django :D
    name = String()
    shares = PositiveInteger()
    price = Float()
    # Names are set from dict keys

    # If you use some keyword(s) again you get exception because of
    # NoDuplicateOrderedDict
    # price = Float()
    """
    It seems like the following
    clsdict = OrderedDict(
        ('name', <class 'String'>),
        ('shares', <class 'PositiveInteger'>),
        ('price', <class 'Float'>)
    )
    """


s = Stock(name='Goog', shares=10, price=400.1)


def _make_init(fields):
    """
    Give a list of fields name, make an __init__ method
    """
    code = 'def __init__(self, %s):\n' % ', '.join(fields)
    for name in fields:
        code += '    self.%s = %s\n' % (name, name)
    return code


# Another way for speed (exec)
class StructMetaWithExec(type):
    @classmethod
    def __prepare__(metacls, name, bases):
        """
        It creates and returns dictionary to use for execution of the class
        body.

        An OrderedDict will preserve the definition order
        :param name:
        :param bases:
        :return:
        """
        return NoDuplicateOrderedDict()

    def __new__(cls, name, bases, clsdict):
        # Collect Descriptors and set their names
        fields = [
            key for key, val in clsdict.items()
            if isinstance(val, Descriptor)
        ]
        for name in fields:
            clsdict[name].name = name

        if fields:
            init_code = _make_init(fields)
            exec(init_code, globals(), clsdict)

        # Make the class and signature exactly as before
        clsobj = super().__new__(cls, name, bases, dict(clsdict))
        # We don't need Signature
        return clsobj


class StructureWithExec(metaclass=StructMetaWithExec):
    _fields = []


class StockWithExec(StructureWithExec):
    name = String()
    shares = PositiveInteger()
    price = Float()


print('With exec')
s = StockWithExec('GOOG', 100, 490.1)
# s.name = 10  # Still works type checking so It gets exception


# New Thought
# Could we merge all set methods? (String, PositiveInteger, Float)
