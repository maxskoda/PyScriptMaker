from abc import ABC, abstractmethod


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
    def calcTime(self, inst, current=0):
        pass

    @abstractmethod
    def toolTip(self):
        pass


