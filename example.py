from meta import debug, debugarg, debugmethods


@debugarg(prefix='****')
def add(x, y):
    return x + y


@debugmethods
class Spam:
    def a(self):
        pass

    def b(self):
        pass


# just python3

def add2(x: int, y: int) -> int:
    return x + y


print(add2(2, 3))

# Function annotations


class S:
    def bar(self, x: int):
        pass

    def foo(self, s: str):
        pass


class mydict(dict):
    def __setitem__(self, name, value):
        if name in self:
            val = self[name]
            if not isinstance(val, list):
                val = [val]
            val.append(name, value)
        else:
            super().__setitem__(name, value)


class mymeta(type):
    @classmethod
    def __prepare__(metacls, name, bases):
        return mydict()


class Sp(metaclass=mymeta):
    def bar(self, x: int):
        pass

    def bar(self, x: str):
        pass


