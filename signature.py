# Problem is you can't use keyword arguments with decorator or metaclass
# But with the following methods you can use keyword arguments

from inspect import Parameter, Signature


class Structure:
    _fields = []

    def __init__(self, *args):
        for name, val in zip(self._fields, args):
            setattr(self, name, val)


class Stock(Structure):
    _fields = ['name', 'shares', 'price']


fields = ['name', 'shares', 'price']
prams = [Parameter(name, Parameter.POSITIONAL_OR_KEYWORD) for name in fields]

sig = Signature(prams)
print(sig)


# sig.bind()  binds positional/keyword args to signature
# .arguments is an OrderedDict of passed values
def foo(*args, **kwargs):
    bound = sig.bind(*args, **kwargs)
    for name, val in bound.arguments.items():
        print(name, val)


foo(1, 2, 3)

# We can use with keyword arguments
foo(1, price=40.1, shares=1)


def make_signature(names):
    return Signature(
        Parameter(name, Parameter.POSITIONAL_OR_KEYWORD) for name in names)


class Structure:
    # Base class
    __signature__ = make_signature([])

    def __init__(self, *args, **kwargs):
        bound = self.__signature__.bind(*args, **kwargs)
        for name, val in bound.arguments.items():
            setattr(self, name, val)


class Stock(Structure):
    __signature__ = make_signature(['name', 'shares', 'price'])


s = Stock('GOOG', 100, 490.1)
print(s.name)

# Or we can use with keyword arguments
s = Stock(name='GOOG', price=490.1, shares=10)
print(s.shares)


# Class decorator solution
def add_signature(*names):
    def decorate(cls):
        cls.__signature__ = make_signature(names)
        return cls

    return decorate


# Usage
@add_signature('name', 'shares', 'price')
class Stock(Structure):
    pass


@add_signature('x', 'y')
class Point(Structure):
    pass


# Metaclass solution
class StructMeta(type):
    def __new__(cls, name, bases, clsdict):
        clsobj = super().__new__(cls, name, bases, clsdict)
        # Read _fields attribute and make a proper signature out of it
        sig = make_signature(clsobj._fields)
        # Set attribute
        setattr(clsobj, '__signature__', sig)
        return clsobj


class Structure2(metaclass=StructMeta):
    _fields = []

    def __init__(self, *args, **kwargs):
        bound = self.__signature__.bind(
            *args,
            **kwargs
        )
        for name, val in bound.arguments.items():
            setattr(self, name, val)


class Stock2(Structure2):
    # It's back to original 'simple' solution
    # Signature are created behind scenes
    _fields = ['name', 'shares', 'price']


s = Stock2('GOOG2', shares=44.1, price=20)
print(s.shares)


# Advice
# Use a class decorator if the goal is to tweak classes that might be unrelated
# Use a metaclass if you're trying to perform action in combination
#  with inheritance
# Don't be so quick to dismiss techniques
# All of the tools are meant to work together


# Problem: Correctness

# You can upgrade attributes to have checks

# It works, but it quickly gets annoying
class StockGetterSetter(Structure2):
    _fields = ['name', 'shares', 'price']

    @property
    def shares(self):
        # Getter
        return self._shares

    @shares.setter
    def shares(self, value):
        # Setter
        if not isinstance(value, int):
            raise TypeError('excepted int')

        if value < 0:
            raise ValueError('must be >=0')

        self._shares = value


# Imagine writing same code for many attributes

# - Want to simplify, but how?
# - Two kinds of checking are intertwined
# - Type checking: int, float, str, etc.
# - Validation: >, >=, <, <=, !=, etc.
# - Question: How to structure it?

# Descriptor Protocol

# - Properties are implemented via descriptors


class Descriptor:
    def __init__(self, name=None):
        # name of attribute being stored. A key in the instance dict.
        self.name = name

    def __get__(self, instance, cls):
        # instance: is the instance being manipulated
        # e.g. Stock instance
        print("Get", self.name)
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        print("Set", self.name, value)
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        print("Delete", self.name)
        del self.__dict__[self.name]


# - Customized processing of attribute access

class StockWithDescriptor(Structure2):
    _fields = ['name', 'shares', 'price']
    name = Descriptor('name')
    shares = Descriptor('shares')  # Redefine .shares
    price = Descriptor('price')


s = StockWithDescriptor('GOOG', 100, 490.1)
# Output: set shares 100
share = s.shares
# Output: Get shares
# del s.shares
# Output: Delete shares
s.shares = 50


# Output: Set shares 50


# Type Checking
class Typed(Descriptor):
    ty = object

    def __set__(self, instance, value):
        # Check type
        if not isinstance(value, self.ty):
            raise TypeError('Expected %s' % self.ty)
        # Class Descriptor set method
        super().__set__(instance, value)


class Integer(Typed):
    ty = int


class Float(Typed):
    ty = float


class String(Typed):
    ty = str


class StockWithInstance(Structure2):
    _fields = ['name', 'shares', 'price']
    name = String('name')
    shares = Integer('shares')
    price = Float('price')


s = StockWithInstance('GOOG3', 100, 490.1)


# s.name = 10 => It gives TypeError


class Positive(Descriptor):
    def __set__(self, instance, value):
        if value < 0:
            raise ValueError('Must be >= 0')
        super().__set__(instance, value)


class PositiveInteger(Integer, Positive):
    pass


print(PositiveInteger.__mro__)
# This chain defines the order in which the value is checked by different
# __set__() methods
# Output:
# (<class '__main__.PositiveInteger'>,
# <class '__main__.Integer'>,
# <class '__main__.Typed'>,
# <class '__main__.Positive'>,
# <class '__main__.Descriptor'>,
# <class 'object'>)
