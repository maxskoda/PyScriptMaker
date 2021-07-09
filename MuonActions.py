# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 21:30:47 2020

@author: Maximilian Skoda
"""
import json
from datetime import datetime
import ScriptActionClass as ScriptActionClass

# instruments
instruments = ["INTER", "SURF", "PolRef", "OffSpec", "CRISP"]


# actions list items need to match method names (obsolete due to abstract class:
# actions = ["RunAngles", "Inject", "ContrastChange", "Transmission", "GoToPressure", "SetJulabo"]


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def tofloat(value):
    try:
        float(value)
        return float(value)
    except ValueError:
        return "NaN"


def writeHeader(samples, args=[]):
    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y, at %H:%M:%S")
    ## for OpenGenie
    outString = "### This script was generated on " + current_time + "\n" + \
                "### with ScriptMaker (c) Maximilian Skoda 2020 \n" + \
                "### Enjoy and use at your own risk. \n\n" + \
                "from genie_python.genie_script_generator import ScriptDefinition, cast_parameters_to\n" + \
                "from genie_python import genie as g\n" + \
                "import numpy as np\n" +\
                "from enum import Enum\n"
    sampList = []

    outString += "class SetDefinition(Enum):\n" + \
                 "...\n\n" +\
                 "def magnet_device_type(magnet_device):\n" +\
                 "...\n" + \
                 "class DoRun(ScriptDefinition):\n\n" + \
                 "def runsscript():\n" +\
                 "\tscript_definition = DoRun()\n"
    return outString


def writeFooter(samples):
    outString = ""
    return outString


class standard_run(ScriptActionClass.ActionClass):
    def __init__(self, start_temperature="keep", stop_temperature="keep", step_temperature=0,
                 start_field="keep", stop_field="keep", step_field=0,
                 custom="None", mevents=10, magnet_device="N/A"):
        # self.Sample = "" # dummy
        self.start_temperature = start_temperature
        self.stop_temperature = stop_temperature
        self.step_temperature = step_temperature
        self.start_field = start_field
        self.stop_field = stop_field
        self.step_field = step_field
        self.custom = custom
        self.mevents = mevents
        self.magnet_device = magnet_device

    def makeAction(self, node):
        # self.Sample = node.child(0, 1).text()
        self.start_temperature = node.child(0, 1).text()
        self.stop_temperature = node.child(1, 1).text()
        self.step_temperature = node.child(2, 1).text()
        self.start_field = node.child(3, 1).text()
        self.stop_field = node.child(4, 1).text()
        self.step_field = node.child(5, 1).text()
        self.custom = node.child(6, 1).text()
        self.mevents = node.child(7, 1).text()
        self.magnet_device = node.child(8, 1).text()
        return self

    def isValid(self):
        if self.magnet_device not in ['ZF', 'LF', 'TF', "N/A"]:
            return [False, "magnet_device must be one of ['ZF', 'LF', 'TF', 'N/A']"]
        else:
            return [True, "All good!"]

    def summary(self):
        return 'Ti={}, Tf={}, T_step={}; ' \
               'Hi={}, Hf={}, H_step={}; ' \
               'mevents={}; magnet={}'.format(self.start_temperature, self.stop_temperature, self.step_temperature,
                                              self.start_field, self.stop_field, self.step_field,
                                              self.custom, self.mevents, self.magnet_device)

    def stringLine(self, sampleNumber):
        outString = "\tscript_definition.run(**{\'start_temperature\': " + self.start_temperature
        outString += ", \'magnet_device\': " + self.magnet_device
        outString += ", \'custom\': " + self.custom
        outString += ", \'start_field\': " + self.start_field
        outString += ", \'mevents\': " + self.mevents
        outString += ", \'stop_field\': " + self.stop_field
        outString += ", \'step_field\': " + self.step_field
        outString += ", \'step_temperature\': " + self.step_temperature
        outString += ", \'stop_temperature\': " + self. stop_temperature + "})"
        return outString

    def calcTime(self, inst):
        # NEED TO THINK ABOUT HOW TO ESTIMATE TIME!!!!
        return 0

    def makeJSON(self):
        pass

    def toolTip(self):
        pass



class IterRegistry(type):
    def __iter__(cls):
        return iter(cls._registry)


class NRsample(object):
    __metaclass__ = IterRegistry
    _registry = []

    def __init__(self, row=[]):
        self._registry.append(self)

        self.title = row[0]
        self.translation = row[1]
        self.height = row[2]
        self.phi_offset = row[3]
        self.psi = row[4]
        self.footprint = row[5]
        self.resolution = row[6]
        self.coarse_noMirror = row[7]
        self.switch_pos = row[8]
        # sampleNumber += 1

    # sampleNumber=0


if __name__ == '__main__':
    print('This is the NR actions module.\n\nDefined actions are: ')
    actions = [cls.__name__ for cls in ScriptActionClass.ActionClass.__subclasses__()]
    print(actions)