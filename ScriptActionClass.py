from abc import ABC, abstractmethod


class AbstractClassExample(ABC):

    @abstractmethod
    def do_something(self):
        print("Some implementation!")


class AnotherSubclass(AbstractClassExample):

        def do_something(self):
            super().do_something()
            print("The enrichment from AnotherSubclass")

class ActionClass(ABC):

    @abstractmethod
    def makeAction(self, node):
        pass

    @abstractmethod
    def summary(self, node):
        pass

    @abstractmethod
    def isValid(self):
        pass

    @abstractmethod
    def stringLine(self, sampleNumber):
        pass

    @abstractmethod
    def summary(self):
        pass

    @abstractmethod
    def makeJSON(self):
        pass

    @abstractmethod
    def calcTime(self, inst):
        pass

    @abstractmethod
    def toolTip(self):
        pass

# Driver code
# for cls in AbstractClassExample.__subclasses__():
#     print (cls.__name__)
# print( issubclass(AnotherSubclass, AbstractClassExample))
# print( isinstance(AnotherSubclass(), AbstractClassExample))
