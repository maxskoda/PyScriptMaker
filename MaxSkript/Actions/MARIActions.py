# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 21:30:47 2020

@author: Maximilian Skoda
"""
import json
from datetime import datetime
import ScriptActionClass as ScriptActionClass



# instruments
instruments = ["MARI", "Iris", "LET", "MAPS", "Merlin", "Osiris", "Tosca", "Vesuvio"]


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
                "import os\n"
    outString += r'sys.path.insert(0, os.path.abspath(os.path.join(r"C:\\", "Instrument", "scripts")))'
    outString += "\nfrom genie_python import genie as g\n"
    outString += "import inst\n\n\n"
    outString += "def runscript():\n"




    return outString

def writeFooter(samples):
    ## for Python
    outString = ""
    return outString


class SampleLoop(ScriptActionClass.ActionClass):
    def __init__(self, samples="S1, S2", Subtitle="", Angles=[0.7, 2.3], uAmps=[5, 20], contrastChange_to="H2O",
                 Flow=1.5, Volume=15.0, wait="False"):
        self.samples = samples.split(",") # model.item(row).child(0,1).text()
        self.Subtitle = Subtitle  # model.item(row).child(1,1).text()
        self.Angles = Angles  # model.item(row).child(2,1).text()
        self.uAmps = uAmps  # model.item(row).child(3,1).text()
        self.Inject = contrastChange_to
        self.flow = tofloat(Flow)
        self.volume = tofloat(Volume)
        self.wait = wait

    def makeAction(self, node):
        self.samples = node.child(0, 1).text().split(",")
        self.Subtitle = node.child(1, 1).text()

        tempAngles = node.child(2, 1).text().split(",")
        self.Angles = [float(a) for a in tempAngles if isfloat(a)]

        tempAmps = node.child(3, 1).text().split(",")
        self.uAmps = [float(a) for a in tempAmps if isfloat(a)]

        self.Inject = node.child(4, 1).text()
        self.flow = tofloat(node.child(5, 1).text())
        self.volume = tofloat(node.child(6, 1).text())
        self.wait = node.child(7, 1).text()
        return self

    def summary(self):
        degree = str(b'\xc2\xb0', 'utf8')
        res1 = dict(zip(self.Angles, self.uAmps))
        res = ''.join("({}{}: {}\u03BCA) ".format(angle, degree, int(uamps)) for angle, uamps in res1.items())
        outString = ''.join(self.samples) + " " + \
                    self.Subtitle + \
                    "\t" + str(res) +\
                    "->" + self.Inject
        return outString

    def isValid(self):
        if len(self.Angles) != len(self.uAmps):
            return [False, "Number of Angles is not the same as number of uAmps or empty."]
        elif any(i > 5 for i in self.Angles):
            return [False, "One of the angles might be too high."]
        elif len(self.Angles) == 0:
            return [False, "Please enter at least on angle/uAmp pair."]
        else:
            return [True, "All good!"]

    def stringLine(self, sampleNumber):
        outString = "\tsamplist = [" + ", ".join(self.samples) + "]\n"
        outString += "\tfor samp in ['sample_' + s for s in samplist]:\n"
        # outString = "##### Sample " + str(sampleNumber) + "\n"
        outString += "\t\tsamp.subtitle = \"" + self.Subtitle + "\"\n"

        for a in range(len(self.Angles)):
            outString += "\t\trun_angle(samp, angle=" \
                         + str(self.Angles[a]) + ", count_uamps=" + str(self.uAmps[a]) + ", mode=\"NR\")\n"

        # Change the contrast:
        outString += "\t\tinject:wait(samp, \"" + self.Inject + \
                    "\", " + str(self.flow) + ", " + str(self.volume) + ")\n"

        return outString

    def makeJSON(self):
        rdict = {"RunAngles": [{"label": "Sample", "value": str(self.Sample)}, \
                               {"label": "Subtitle", "value": str(self.Subtitle)}, \
                               {"label": "Angles", "value": ['{:.1f}'.format(x) for x in self.Angles]}, \
                               {"label": "uAmps", "value": ['{}'.format(x) for x in self.uAmps]}]}
        return json.dumps(rdict, indent=4)

    def calcTime(self, inst):
        if inst in ["INTER", "POLREF", "OFFSPEC"]:
            return sum(self.uAmps) * len(self.samples) / 40.0 * 60
        else:
            return sum(self.uAmps) * len(self.samples) / 180.0 * 60

    def toolTip(self):
        return "Number of Angles and uAmps entries need to be the same."

class setCCR(ScriptActionClass.ActionClass):
    def __init__(self, Temperature="200.0", lowLimit="", highLimit="", wait=5):
        self.temperature = Temperature
        self.lowLimit = lowLimit
        self.highLimit = highLimit
        self.wait = wait

    def makeAction(self, node):
        self.temperature = node.child(0, 1).text()
        self.lowLimit = node.child(1, 1).text()
        self.highLimit = node.child(2, 1).text()
        self.wait = node.child(3, 1).text()
        return self

    def isValid(self):
        if (1.0 < float(self.temperature) < 390.0) and self.lowLimit == "" and self.highLimit == "":
            return [True]
        elif (1.0 < float(self.temperature) < 390.0) and (
                float(self.lowLimit) < float(self.temperature) < float(self.highLimit)):
            return [True]
        else:
            return [False]

    def summary(self):
        if self.lowLimit == "" and self.highLimit == "":
            return '{}'.format(self.temperature)
        else:
            return '{} (min={}, max={})'.format(self.temperature, self.lowLimit, self.highLimit)

    def stringLine(self, sampleNumber):
        outString = "\t### Setting CCR \n"
        if str(self.lowLimit) == "" and str(self.highLimit == ""):
            outString += "\tg.cset(CCR_head= " + str(self.temperature) + ")\n"
            outString += "\tg.waitfor(CCR_head=" + str(self.temperature) + ")\n"
        else:
            outString += "\tg.cset(CCR_head= " + str(self.temperature) + \
                        ", lowLimit=" + str(self.lowLimit) + \
                        ", highLimit=" + str(self.highLimit) + ")\n"
            outString += "\tg.waitfor(CCR_head=" + str(self.temperature) + \
                        ", lowLimit=" + str(self.lowLimit) + \
                        ", highLimit=" + str(self.highLimit) + ")\n"
        return outString

    def calcTime(self, inst):
        # NEED TO THINK ABOUT HOW TO ESTIMATE TIME
        return 0

    def makeJSON(self):
        pass

    def toolTip(self):
        pass

class doRun(ScriptActionClass.ActionClass):
    def __init__(self, sample_name="", ei=120, freq=350, sng='True', uAmps=1000):
        self.sample_name = sample_name
        self.ei = ei
        self.freq = freq
        self.sng = sng
        self.uAmps = uAmps

    def makeAction(self, node):
        self.sample_name = node.child(0, 1).text()
        self.ei = node.child(1, 1).text()
        self.freq = node.child(2, 1).text()
        self.sng = node.child(3, 1).text()
        self.uAmps = node.child(4, 1).text()
        return self

    def isValid(self):
        return [True, "All good!"]

    def summary(self):
        return '{} - Ei={}meV, Freq={}Hz'.format(self.sample_name, self.ei, self.freq)

    def stringLine(self, sampleNumber):
        outString = "\t### run\n"
        outString += "\tinst.set_ei(" + str(self.ei) + ", " + self.freq + ", 'g', single=" + self.sng + ", disk=0)\n"
        outString += "\tg.waitfor(minutes=5)\n\n"
        outString += "\tg.begin()\n"
        outString += "\tg.change_title(f'" + '{} - Ei={}meV, Freq={}Hz'.format(self.sample_name, self.ei, self.freq) + "')\n"
        outString += "\tg.waitfor(uamps=" + self.uAmps + ")\n"
        outString += "\tg.end()\n\n"
        return outString

    def calcTime(self, inst):
        return 0#sum(self.uAmps) / 180.0 * 60

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
        #sampleNumber += 1
        
    #sampleNumber=0


if __name__ == '__main__':
    print('This is the NR actions module.\n\nDefined actions are: ')
    actions = [cls.__name__ for cls in ScriptActionClass.ActionClass.__subclasses__()]
    print(actions)