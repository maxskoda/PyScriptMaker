# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 16:50:47 2021

@author: Maximilian Skoda
"""
import json
from datetime import datetime
import MaxSkript.Actions.ScriptActionClass as ScriptActionClass



# instruments
instruments = ["SANS2D", "LARMOR", "LOQ"]
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
                "import sys\n" + \
                "import os\n" + \
                "from genie_python import genie as g, BLOCK_NAMES as b\n" + \
                "sys.path.append(r\"c:\instrument\scripts\")\n" + \
                "from instrument.larmor import * # pylint: disable=wildcard-import, unused-wildcard-import\n\n"

    # outString += r'sys.path.insert(0, os.path.abspath(os.path.join(r"C:\\", "Instrument", "scripts")))'
    # outString += "\nfrom genie_python import genie as g\n"
    # outString += "from technique.reflectometry import SampleGenerator, run_angle, contrast_change, transmission\n\n\n"
    outString += "def example_script():\n"

    return outString

def writeFooter(samples):
    ## for Python
    outString = ""
    return outString

class do_trans(ScriptActionClass.ActionClass):
    # action_type = 'multi'
    def __init__(self, title="", pos="", uamps=3, thickness=2):
        self.title = title
        self.pos = pos
        self.uamps = int(uamps)
        self.thickness = thickness

    def makeAction(self, node):
        self.title = node.child(0, 1).text()
        self.pos = node.child(1, 1).text()
        self.uamps = node.child(2, 1).text()
        self.thcikness = node.child(3, 1).text()

        return self

    def summary(self):
        res = ''.join("{} -- {} -- {}uAmps ".format(self.title, self.pos, self.uamps))
        outString = str(res)
        return outString
        
    def isValid(self):
        return [True, "All good!"]
        
    def stringLine(self, sampleNumber):
        outString = "\tdo_trans(title='{" + self.title + "}', pos='" + self.pos + \
                    "', uamps=" + str(self.uamps) + ", thickness=" + str(self.thickness) +")\n"
        return outString
    
    def makeJSON(self):
        rdict = {"do_trans": [{ "label": "title", "value": str(self.title) },\
                       { "label": "pos", "value": str(self.pos) },\
                       { "label": "uamps", "value": str(self.uamps)},\
                       {"label": "thickness", "value": str(self.thickness)}]}
        return json.dumps(rdict, indent=4)

    def calcTime(self, inst):
        if inst in ["SANS2D", "LARMOR"]:
            return int(self.uamps) / 40.0 * 60
        else:
            return int(self.uamps) / 180.0 * 60

    def toolTip(self):
        return "Number of Angles and uAmps entries need to be the same."


class do_sans(ScriptActionClass.ActionClass):
    # action_type = 'multi'
    def __init__(self, title="", pos="", uamps=3, thickness=2, dae='event'):
        self.title = title
        self.pos = pos
        self.uamps = int(uamps)
        self.thickness = thickness
        self.dae = dae

    def makeAction(self, node):
        self.title = node.child(0, 1).text()
        self.pos = node.child(1, 1).text()
        self.uamps = node.child(2, 1).text()
        self.thickness = node.child(3, 1).text()
        self.event = node.child(4, 1).text()

        return self

    def summary(self):
        res = ''.join("{} -- {} -- {}uAmps {}".format(self.title, self.pos, self.uamps, self.dae))
        outString = str(res)
        return outString

    def isValid(self):
        return [True, "All good!"]

    def stringLine(self, sampleNumber):
        outString = "\tdo_sans(title='{" + self.title + "}', pos='" + self.pos + \
                    "', uamps=" + self.uamps + ", thickness=" + self.thickness + ", dae='" + self.dae + "')\n"
        return outString

    def makeJSON(self):
        rdict = {"do_sans": [{"label": "title", "value": str(self.title)}, \
                              {"label": "pos", "value": str(self.pos)}, \
                              {"label": "uamps", "value": str(self.uamps)}, \
                              {"label": "thickness", "value": str(self.thickness)}, \
                              {"label": "dae", "value": self.dae}
                              ]}
        return json.dumps(rdict, indent=4)

    def calcTime(self, inst):
        if inst in ["SANS2D", "LARMOR"]:
            return int(self.uamps) / 40.0 * 60
        else:
            return int(self.uamps) / 180.0 * 60

    def toolTip(self):
        return "Number of Angles and uAmps entries need to be the same."


if __name__ == '__main__':
    print('This is the SANS actions module.\n\nDefined actions are: ')
    actions = [cls.__name__ for cls in ScriptActionClass.ActionClass.__subclasses__()]
    print(actions)