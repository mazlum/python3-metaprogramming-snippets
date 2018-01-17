from functools import wraps
import logging
import os


def debug(func):
    # func is function to be wrapped
    # wraps copies metada
    # -- name and docstring
    # -- function attributes
    # if 'DEBUG' not in os.environ:
    #    return func

    msg = func.__name__

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(msg)
        return func(*args, **kwargs)

    return wrapper


def debugarg(prefix=''):
    def decorate(func):
        msg = prefix + func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            print(msg)
            return func(*args, **kwargs)

        return wrapper

    return decorate


# Class decorator
def debugmethods(cls):
    for name, val in vars(cls).items():
        # Get callable items(methods)
        if callable(val):
            setattr(cls, name, debug(val))
    return cls


# metaclass
class debugmeta(type):
    # All values in Python have a type
    # Classes define new types
    # Classes are instances of types
    def __new__(cls, clsname, bases, clsdict):
        clsobj = super().__new__(cls, clsname, bases, clsdict)
        clsobj = debugmethods(clsobj)
        return clsobj


# Usage
# class Base(metaclass=debugmeta):
# class Spam(Base):
# ...
# Default
# Class Spam(metaclass=type)
# ...
# By default it's set to 'type' but yu can change it to something else


class mtype(type):
    def __new__(cls, clsname, bases, clsdict):
        if len(bases) > 1:
            raise TypeError('NO!')
        return super().__new__(cls, clsname, bases, clsdict)


class Base(metaclass=mtype):
    pass



