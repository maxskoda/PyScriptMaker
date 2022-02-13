# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 21:30:47 2020

@author: Maximilian Skoda
"""
import os.path
import json
from datetime import datetime
import PyQt5.QtCore
import MaxSkript.Actions.ScriptActionClass as ScriptActionClass


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


def isint(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def tofloat(value):
    try:
        float(value)
        return float(value)
    except ValueError:
        return "NaN"


def writeHeader(samples, cols=[]):
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
    outString += "from technique.reflectometry import SampleGenerator, run_angle, contrast_change, transmission\n\n\n"
    outString += "def runscript(dry_run=False):\n"

    outString += "\tsample_generator = SampleGenerator(\n" + \
                 "\t\t    translation = 400.0,\n" + \
                 "\t\t height2_offset = 0.0,\n" + \
                 "\t\t     phi_offset = 0.0,\n" + \
                 "\t\t     psi_offset = 0.0,\n" + \
                 "\t\t  height_offset = 0.0,\n" + \
                 "\t\t     resolution = 0.03,\n" + \
                 "\t\t      footprint = 60,\n" + \
                 "\t\t          valve = 1)\n\n"
    sampList=[]

    for i, samp in enumerate(samples):
        outString += "\tsample_" + str(i+1) + " = sample_generator.new_sample(title=" #samples[samp].get("Sample/Title")
        outString += r'"' + samp.get("Sample/Title") + r'",' + "\n"
        outString += "\t\t   translation = " + samp.get("Trans") +",\n"
        outString += "\t\t height_offset = " + samp.get("Height")
        if len(cols):
            if 3 in cols:
                outString += "\,\n\t\t    phi_offset = " + samp.get("Phi Offset")
            if 4 in cols:
                outString += ",\n\t\t    psi_offset = " + samp.get("Psi")
            if 5 in cols:
                outString += ",\n\t\t     footprint = " + samp.get("Footprint")
            if 6 in cols:
                outString += ",\n\t\t    resolution = " + samp.get("Resolution")
            if 7 in cols:
                outString += ",\n\t\theight2_offset = " + samp.get("Coarse_noMirror")
            if 8 in cols:
                outString += ",\n\t\t         valve = " + samp.get("Switch")
        else:
            outString += ",\n\t\t    phi_offset = " + samp.get("Phi Offset")
            outString += ",\n\t\t    psi_offset = " + samp.get("Psi")
            outString += ",\n\t\t     footprint = " + samp.get("Footprint")
            outString += ",\n\t\t    resolution = " + samp.get("Resolution")
            outString += ",\n\t\theight2_offset = " + samp.get("Coarse_noMirror")
            outString += ",\n\t\t         valve = " + samp.get("Switch")

        outString += ")\n\n"


    return outString


def writeFooter(samples):
    ## for Python
    outString = ""
    return outString


class RunAngles(ScriptActionClass.ActionClass):
    action_type = 'multi'
    def __init__(self, Sample="", Subtitle="", Angles=[0.7, 2.3], uAmps=[5, 20], options=''):
        self.Sample = Sample #model.item(row).child(0,1).text()
        self.Subtitle = Subtitle #model.item(row).child(1,1).text()
        self.Angles = Angles #model.item(row).child(2,1).text()
        self.uAmps = uAmps #model.item(row).child(3,1).text()
        self.options = options

    def get_icon(self):
        return "Running_icon.svg"

    def set_countrate(self, rate):
        countRate = rate
        print("CT: ", countRate)

    def makeAction(self, node):
        self.Sample = node.child(0, 1).text()
        self.Subtitle = node.child(1, 1).text()

        tempAngles = node.child(2, 1).text().split(",")
        self.Angles = [float(a) for a in tempAngles if isfloat(a)]

        tempAmps = node.child(3, 1).text().split(",")
        self.uAmps = [float(a) for a in tempAmps if isfloat(a)]

        self.options = node.child(4, 1).text().split(",")
        return self

    def summary(self):
        degree = str(b'\xc2\xb0', 'utf8')
        res1 = dict(zip(self.Angles, self.uAmps))
        res = ''.join("({}{}: {}\u03BCAh) ".format(angle, degree, int(uamps)) for angle, uamps in res1.items())
        outString = self.Sample + " " +\
                    self.Subtitle + "\t|"\
                    "\t" + str(res)
        return outString
        
    def isValid(self):
        if len(self.Angles) != len(self.uAmps):
            return [False, "Number of Angles is not the same as number of uAmps or empty."]
        elif any(i > 5 for i in self.Angles):
            return [False, "One of the angles might be too high."]
        elif len(self.Angles) == 0:
            return [False, "Please enter at least on angle/uAmp pair."]
        elif not set(self.options).issubset(set(['', "\'\'", 'SM', 't', 'ah', 'solid'])):
            return [False, "Valid options are: '', 'SM', 't', 'ah', 'solid'"]
        else:
            return [True, "All good!"]
        
    def stringLine(self, sampleNumber):
        outString = "\t##### Sample " + str(sampleNumber) + "\n"
        outString += "\tsample_" + str(sampleNumber) + ".subtitle=" + "\"" + self.Subtitle + "\"\n"
        
        for a in range(len(self.Angles)):
            outString += "\trun_angle(sample_" + str(sampleNumber) + ", " \
                         + str(self.Angles[a]) + ", count_uamps=" + str(self.uAmps[a]) + ")\n"#", mode=\"NR\")\n"
        return outString
    
    def makeJSON(self):
        rdict = {"RunAngles": [{ "label": "Sample", "value": str(self.Sample) },\
                       { "label": "Subtitle", "value": str(self.Subtitle) },\
                       { "label": "Angles", "value": ['{:.2f}'.format(x) for x in self.Angles]},\
                       { "label": "uAmps", "value": ['{}'.format(x) for x in self.uAmps]}, \
                       {"label": "Options", "value": [] if '' in self.options else ['{}'.format(x) for x in self.options]}]}
        return json.dumps(rdict, indent=4)

    def calcTime(self, inst):
        if inst.upper().upper() in ["INTER", "POLREF", "OFFSPEC"]:
            return sum(self.uAmps) / 40.0 * 60
        else:
            return sum(self.uAmps) / 180.0 * 60

    def toolTip(self):
        return "Number of Angles and uAmps entries need to be the same."


class RunAngles_SM(ScriptActionClass.ActionClass):
    action_type = 'multi'

    def __init__(self, Sample="", Subtitle="", Angles=[0.7, 2.3], uAmps=[5, 20], options=''):
        self.Sample = Sample  # model.item(row).child(0,1).text()
        self.Subtitle = Subtitle  # model.item(row).child(1,1).text()
        self.Angles = Angles  # model.item(row).child(2,1).text()
        self.uAmps = uAmps  # model.item(row).child(3,1).text()
        self.options = options

    def get_icon(self):
        return "Running_icon.svg"

    def set_countrate(self, rate):
        countRate = rate
        print("CT: ", countRate)

    def makeAction(self, node):
        self.Sample = node.child(0, 1).text()
        self.Subtitle = node.child(1, 1).text()

        tempAngles = node.child(2, 1).text().split(",")
        self.Angles = [float(a) for a in tempAngles if isfloat(a)]

        tempAmps = node.child(3, 1).text().split(",")
        self.uAmps = [float(a) for a in tempAmps if isfloat(a)]

        self.options = node.child(4, 1).text().split(",")
        return self

    def summary(self):
        degree = str(b'\xc2\xb0', 'utf8')
        res1 = dict(zip(self.Angles, self.uAmps))
        res = ''.join("({}{}: {}\u03BCAh) ".format(angle, degree, int(uamps)) for angle, uamps in res1.items())
        outString = self.Sample + " " + \
                    self.Subtitle + \
                    "\t" + str(res)
        return outString

    def isValid(self):
        if len(self.Angles) != len(self.uAmps):
            return [False, "Number of Angles is not the same as number of uAmps or empty."]
        elif any(i > 5 for i in self.Angles):
            return [False, "One of the angles might be too high."]
        elif len(self.Angles) == 0:
            return [False, "Please enter at least on angle/uAmp pair."]
        elif not set(self.options).issubset(set(['', "\'\'", 'SM', 't', 'ah', 'solid'])):
            return [False, "Valid options are: '', 'SM', 't', 'ah', 'solid'"]
        else:
            return [True, "All good!"]

    def stringLine(self, sampleNumber):
        outString = "\t##### Sample " + str(sampleNumber) + "\n"
        outString += "\tsample_" + str(sampleNumber) + ".subtitle=" + "\"" + self.Subtitle + "\"\n"

        for a in range(len(self.Angles)):
            outString += "\trun_angle_SM(sample_" + str(sampleNumber) + ", " \
                         + str(self.Angles[a]) + ", count_uamps=" + str(self.uAmps[a]) + ")\n"  # ", mode=\"NR\")\n"
        return outString

    def makeJSON(self):
        rdict = {"RunAngles": [{"label": "Sample", "value": str(self.Sample)}, \
                               {"label": "Subtitle", "value": str(self.Subtitle)}, \
                               {"label": "Angles", "value": ['{:.2f}'.format(x) for x in self.Angles]}, \
                               {"label": "uAmps", "value": ['{}'.format(x) for x in self.uAmps]}, \
                               {"label": "Options", "value": ['{}'.format(x) for x in self.options]}]}
        return json.dumps(rdict, indent=4)

    def calcTime(self, inst):
        if inst.upper().upper() in ["INTER", "POLREF", "OFFSPEC"]:
            return sum(self.uAmps) / 40.0 * 60
        else:
            return sum(self.uAmps) / 180.0 * 60

    def toolTip(self):
        return "Number of Angles and uAmps entries need to be the same."


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
        if inst.upper() in ["INTER", "POLREF", "OFFSPEC"]:
            return sum(self.uAmps) * len(self.samples) / 40.0 * 60
        else:
            return sum(self.uAmps) * len(self.samples) / 180.0 * 60

    def toolTip(self):
        return "Number of Angles and uAmps entries need to be the same."

#
# class run_angle_polref(ScriptActionClass.ActionClass):
#     def __init__(self, sample_stack="", angles=[0.5, 1.6], Subtitle="",
#                  frames=[36000, 36000], number_of_runs=[1, 4], pol_mode='PNR'):
#         self.Sample = sample_stack  # model.item(row).child(0,1).text()
#         self.Subtitle = Subtitle  # model.item(row).child(1,1).text()
#         self.angles = angles  # model.item(row).child(2,1).text()
#         self.frames = frames  # model.item(row).child(3,1).text()
#         self.runs = number_of_runs
#         self.pol_mode = pol_mode
#
#     def makeAction(self, node):
#         self.Sample = node.child(0, 1).text()
#         self.Subtitle = node.child(1, 1).text()
#
#         tempAngles = node.child(2, 1).text().split(",")
#         self.angles = [float(a) for a in tempAngles if isfloat(a)]
#
#         temp_frames = node.child(3, 1).text().split(",")
#         self.frames = [float(a) for a in temp_frames if isfloat(a)]
#
#         self.runs = node.child(4, 1).text()
#         return self
#
#     def summary(self):
#         degree = str(b'\xc2\xb0', 'utf8')
#         res1 = dict(zip(self.angles, self.frames))
#         res = ''.join("({}{}: {}frames) ".format(angle, degree, int(frames)) for angle, frames in res1.items())
#         outString = self.Sample + " " + \
#                     self.Subtitle + \
#                     "\t" + str(res)
#         return outString
#
#     def isValid(self):
#         if len(self.angles) != len(self.frames):
#             return [False, "Number of Angles is not the same as number of uAmps or empty."]
#         elif any(i > 5 for i in self.angles):
#             return [False, "One of the angles might be too high."]
#         elif len(self.angles) == 0:
#             return [False, "Please enter at least on angle/uAmp pair."]
#         else:
#             return [True, "All good!"]
#
#     def stringLine(self, sampleNumber):
#         outString = "##### Sample " + str(sampleNumber) + "\n"
#         outString += "angles = " + str(self.angles) + "\n"
#         outString += "frames = " + str(self.frames) + "\n"
#         outString += "runs = [" + str(self.runs) + "]\n"
#         outString += "for angle, frame, run_no in zip(angles, frames, runs):\n"
#         outString += "\tinst.run_angle_polref(angle=angle, number_of_runs=run_no,\n"
#         outString += "\t\t\t\t\t\trun_frames=frame, run_name="+self.Subtitle+")\n"
#         outString += "\t\t\t\t\t\tsample_stack=sample, pol_mode=" + self.pol_mode + ")\n"
#
#         return outString
#
#     def makeJSON(self):
#         rdict = {"RunAngles": [{"label": "Sample", "value": str(self.Sample)}, \
#                                {"label": "Subtitle", "value": str(self.Subtitle)}, \
#                                {"label": "Angles", "value": ['{:.1f}'.format(x) for x in self.angles]}, \
#                                {"label": "frames", "value": ['{}'.format(x) for x in self.frames]}]}
#         return json.dumps(rdict, indent=4)
#
#     def calcTime(self, inst):
#         if inst.upper() in ["INTER", "POLREF", "OFFSPEC"]:
#             return sum(self.uAmps) / 40.0 * 60
#         else:
#             return sum(self.uAmps) / 180.0 * 60
#
#     def toolTip(self):
#         return "Number of Angles and uAmps entries need to be the same."


class Inject(ScriptActionClass.ActionClass):
    def __init__(self, Sample="", Solution="D2O", Flow=1.5, Volume=15.0, wait="False"):
        self.Sample = Sample #model.item(row).child(0,1).text()
        self.solution = Solution
        self.flow = tofloat(Flow)
        self.volume = tofloat(Volume)
        self.wait = wait

    def get_icon(self):
        return "inject.png"
        
    def makeAction(self, node):
        self.Sample = node.child(0, 1).text()
        self.solution = node.child(1, 1).text()
        self.flow = tofloat(node.child(2, 1).text())
        self.volume = tofloat(node.child(3, 1).text())
        self.wait = node.child(4, 1).text()
        return self

    def isValid(self):
        if str(self.solution).upper() in \
                ["D2O", "H2O", "SMW", "SiCM", "SYRINGE_A", "SYRINGE_B"]:
            return [True, "All good!"]
        else:
            return [False, "Requested liquid not valid. Must be D2O, H2O, SMW, SiCM, SYRINGE_A, SYRINGE_B"]
        
    def summary(self):
        if self.wait == 'False':
            w = 'continue'
        else:
            w = 'wait'

        return '{}, {}, {}, {} -> {}'.format(self.Sample, self.solution, self.flow, self.volume, w)
        
    def stringLine(self, sampleNumber):
        ### needs string for 'wait'
        if self.wait != 'False':
            outString = "\tinject:wait(sample_" + str(sampleNumber) + ", \"" + self.solution + \
                        "\", " + str(self.flow) + ", " + str(self.volume) + ")\n"
        else:
            outString = "\tinject(sample_" + str(sampleNumber) + ", \"" + self.solution + \
                        "\", " + str(self.flow) + ", " + str(self.volume) + ")\n"
        return outString
    
    def makeJSON(self):
        rdict = {"Inject": [{ "label": "Sample", "value": str(self.Sample) },\
                   { "label": "Solution", "value": str(self.solution)},\
                   { "label": "Flow", "value": str(self.flow)},\
                   { "label": "Volume", "value": str(self.volume)},\
                   { "label": "Wait", "value": str(self.wait)}]
            }
        return json.dumps(rdict, indent=4)

    def calcTime(self, inst):
        if self.wait == 'False':
            return 0
        else:
            return self.volume/self.flow

    def toolTip(self):
        return "Valid input: D2O, H2O, SMW, SiCM, SYRINGE_A, SYRINGE_B. HPLC: A - D2O, B - H2O"


class ChangeContrast(ScriptActionClass.ActionClass):
    def __init__(self, Sample="", solvent="D2O", Flow=1.5, Volume=15.0, wait=False):
        self.Sample = Sample  # model.item(row).child(0,1).text()
        self.solvent = solvent
        self.flow = tofloat(Flow)
        self.volume = tofloat(Volume)
        self.wait = wait

    def makeAction(self, node):
        self.Sample = node.child(0, 1).text()
        self.solvent = node.child(1, 1).text()
        self.flow = tofloat(node.child(2, 1).text())
        self.volume = tofloat(node.child(3, 1).text())
        self.wait = node.child(4, 1).text()
        return self

    def isValid(self):
        return [True]

    def summary(self):
        return '{}, -->{}, {}, {}'.format(self.Sample, self.solvent, self.flow, self.volume)

    def stringLine(self, sampleNumber):
        if self.wait != 'False':
            outString = u"\tcontrast_change(sample_" + str(sampleNumber) + ".valve, " + self.solvent + \
                        ", " + str(self.flow) + ", " + str(self.volume) + ", wait=True)\n"
        else:
            outString = "\tcontrast_change(sample_" + str(sampleNumber) + ".valve, " + self.solvent + \
                        ", " + str(self.flow) + ", " + str(self.volume) + ")\n"
        return outString

    def makeJSON(self):
        rdict = {"ChangeContrast": [{"label": "Sample", "value": str(self.Sample)},
                                    {"label": "solvent", "value": str(self.solvent)},
                                    {"label": "Flow", "value": str(self.flow)},
                                    {"label": "Volume", "value": str(self.volume)},
                                    {"label": "Wait", "value": str(self.wait)}]
                 }
        return json.dumps(rdict, indent=4)

    def calcTime(self, inst):
        if self.wait == 'False':
            return 0
        else:
            return self.volume/self.flow

    def toolTip(self):
        return "Concentrations in % and need to add up to 100."

    def get_icon(self):
        return "contrast2.png"



class ContrastChange(ScriptActionClass.ActionClass):
    def __init__(self, Sample="", concA=100, concB=0, concC=0, concD=0, Flow=1.5, Volume=15.0, wait=False):
        self.Sample = Sample #model.item(row).child(0,1).text()
        self.concA = concA
        self.concB = concB
        self.concC = concC
        self.concD = concD
        self.flow = tofloat(Flow)
        self.volume = tofloat(Volume)
        self.wait = wait
        
    def makeAction(self, node):
        self.Sample = node.child(0,1).text()
        self.concA = node.child(1,1).text()
        self.concB = node.child(2,1).text()
        self.concC = node.child(3,1).text()
        self.concD = node.child(4,1).text()
        self.flow = tofloat(node.child(5,1).text())
        self.volume = tofloat(node.child(6,1).text())
        self.wait = node.child(7, 1).text()
        return self

    def isValid(self):
        if isfloat(self.concA) and isfloat(self.concB) and isfloat(self.concC) and isfloat(self.concD):
            if float(self.concA) + float(self.concB) + float(self.concC) + float(self.concD) == 100:
                return [True]
            else:
                return [False, "Concentrations do not add up to 100!"]
        else:
            return [False, "Please enter numbers."]
        
    def summary(self):    
        return '{}, {}, {}, {}, {}, {}, {}'.format(self.Sample, self.concA, self.concB, self.concC, self.concD,
                                                   self.flow, self.volume)
        
    def stringLine(self, sampleNumber):
        if self.wait != 'False':
            outString = "\tcontrast_change(sample_" + str(sampleNumber) + ".valve, " + \
                        "[" + self.concA + "," + self.concB + "," + self.concC + "," + self.concD + "]"\
                        ", " + str(self.flow) + ", " + str(self.volume) + ")\n"
        else:
            outString = "\tcontrast_change(sample_" + str(sampleNumber) + ".valve, " + \
                        "[" + self.concA + "," + self.concB + "," + self.concC + "," + self.concD + "]" \
                        ", " + str(self.flow) + ", " + str(self.volume) + "wait=True" + ")\n"
        return outString
    
    def makeJSON(self):
        rdict = {"ContrastChange": [{ "label": "Sample", "value": str(self.Sample) },\
                   { "label": "concA", "value": str(self.concA)},\
                   { "label": "concB", "value": str(self.concB)},\
                   { "label": "concC", "value": str(self.concC)},\
                   { "label": "concD", "value": str(self.concD)},\
                   { "label": "Flow", "value": str(self.flow)},\
                   { "label": "Volume", "value": str(self.volume)}]
            }
        return json.dumps(rdict, indent=4)

    def calcTime(self, inst):
        if self.wait == 'False':
            return 0
        else:
            return self.volume/self.flow

    def toolTip(self):
        return "Concentrations in % and need to add up to 100."


class Transmission(ScriptActionClass.ActionClass):
    def __init__(self, s1vg=1.0, s2vg=0.5, s1hg=50, s2hg=30, Sample="", Subtitle="", uAmps=20, s4hg=53.0, height_offset=5, sm_angle=0.75):
        self.Sample = Sample 
        self.Subtitle = Subtitle 
        self.s1vg = tofloat(s1vg)
        self.s2vg = s2vg
        self.s1hg = s1hg
        self.s2hg = s2hg
        self.s4hg = s4hg
        self.uAmps = uAmps
        self.height_offset = height_offset
        self.sm_angle = sm_angle

    def get_icon(self):
        return "transmission_icon.png"

    def makeAction(self, node):
        self.Sample = node.child(0, 1).text()
        self.Subtitle = node.child(1, 1).text()
        self.s1vg = tofloat(node.child(2, 1).text())
        self.s2vg = tofloat(node.child(3, 1).text())
        self.s1hg = tofloat(node.child(4, 1).text())
        self.s2hg = tofloat(node.child(5, 1).text())
        self.s4hg = tofloat(node.child(6, 1).text())
        self.uAmps = tofloat(node.child(7, 1).text())
        self.height_offset = tofloat(node.child(8, 1).text())
        self.sm_angle = tofloat(node.child(9, 1).text())
        return self

    def summary(self):
        # outString = self.Sample + " " +\
        #             self.Subtitle + " " +\
        #             self.s1vg + " "
                    
        return '{}, {}, {}, {}, {}, {}, {}, {}, {}'.format(self.Sample, self.Subtitle, self.uAmps, self.s1vg, self.s2vg, self.s1hg, self.s2hg, self.height_offset, self.sm_angle)
        
    def isValid(self):
        for attr in self.__dict__:
            if attr == "NaN" or attr == "nan":
                return [False, "Check values! One is not a number."]
                break
        return [True]

    def makeJSON(self):
        rdict = {"Transmission": [{ "label": "Sample", "value": str(self.Sample) },\
                       { "label": "Subtitle", "value": str(self.Subtitle) },\
                       { "label": "uAmps", "value": str(self.uAmps)},\
                       { "label": "s1vg", "value": str(self.s1vg)},\
                       { "label": "s2vg", "value": str(self.s1vg)},\
                       { "label": "s1hg", "value": str(self.s1vg)},\
                       { "label": "s1hg", "value": str(self.s1vg)},\
                       { "label": "height_offset", "value": str(self.height_offset)},\
                       { "label": "sm_angle", "value": str(self.sm_angle)}]}
        return json.dumps(rdict, indent=4)
        
    def stringLine(self, sampleNumber):
        outString = "\ttransmission(sample_" + self.Sample + ", \"" + self.Subtitle + "\", " + str(self.uAmps) + "," + str(self.s1vg) + "," + str(self.s2vg) +\
                                                "," + str(self.s1hg) + "," + str(self.s2hg) + "," + str(self.s4hg)
        if str(self.height_offset) != "":
            outString += "," + str(self.height_offset)
        if str(self.sm_angle) != "":
            outString += "," + str(self.sm_angle)
                                                
        return outString+")\n"

    def calcTime(self, inst):
        if inst.upper() in ["INTER", "POLREF", "OFFSPEC"]:
            return self.uAmps / 40.0 * 60
        else:
            return self.uAmps / 180.0 * 60

    def toolTip(self):
        pass


class GoToPressure(ScriptActionClass.ActionClass):
    def __init__(self, pressure=20.0, speed=15.0, hold=True, wait=True):
        # self.Sample = "" # dummy
        self.pressure = pressure
        self.speed = speed # [cm^2/min]
        self.hold = hold
        self.wait = wait

        
    def makeAction(self, node):
        # self.Sample = node.child(0, 1).text()
        self.pressure = node.child(0, 1).text()
        self.speed = node.child(1, 1).text()
        self.hold = node.child(2, 1).text()
        self.wait = node.child(3, 1).text()
        return self

    def isValid(self):
        return [True]
        
    def summary(self):
        return 'p={} mN,  speed={} cm\u00b2/min'.format(self.pressure, self.speed)
        
    def stringLine(self, sampleNumber):
        outString = "\tgo_to_pressure(" + str(self.pressure) + ", " + str(self.speed)
        if self.hold == 'False':
            outString += ", hold=False"
        if self.wait == 'False':
            outString += ", wait=False"
        outString += ")\n"
        return outString

    def calcTime(self, inst):
        # NEED TO THINK ABOUT HOW TO ESTIMATE TIME!!!!
        return 0

    def makeJSON(self):
        pass

    def toolTip(self):
        pass


class GoToArea(ScriptActionClass.ActionClass):
    def __init__(self, area=600.0, speed=15.0, wait=True):
        # self.Sample = "" # dummy
        self.area = area
        self.speed = speed  # [cm^2/min]
        self.wait = wait

    def makeAction(self, node):
        # self.Sample = node.child(0, 1).text()
        self.area = node.child(0, 1).text()
        self.speed = node.child(1, 1).text()
        self.wait = node.child(2, 1).text()
        return self

    def isValid(self):
        return [True]

    def summary(self):
        return 'a={} cm\u00b2, speed={} cm\u00b2/min'.format(self.area, self.speed)

    def stringLine(self, sampleNumber):
        outString = "\tgo_to_area(" + str(self.area) + ", " + str(self.speed)
        if self.wait == 'False':
            outString += ", wait=False"
        outString += ")\n"
        return outString

    def calcTime(self, inst):
        # assuming a minimum area of 100 (but really need current value):
        return 0 #(tofloat(self.area) - 100) / tofloat(self.speed)

    def makeJSON(self):
        pass

    def toolTip(self):
        pass


class SetJulabo(ScriptActionClass.ActionClass):
    def __init__(self, Temperature="20.0", lowLimit="", highLimit=""):
        self.Sample = ""  # dummy
        self.temperature = Temperature
        self.lowLimit = lowLimit
        self.highLimit = highLimit

    def makeAction(self, node):
        self.Sample = node.child(0, 1).text()
        self.temperature = node.child(1, 1).text()
        self.lowLimit = node.child(2, 1).text()
        self.highLimit = node.child(3, 1).text()
        return self

    def isValid(self):
        if (0.0 < float(self.temperature) < 90.0) and self.lowLimit == "" and self.highLimit == "":
            return [True]
        elif (0.0 < float(self.temperature) < 90.0) and (
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
        print(str(self.lowLimit), self.highLimit)
        if str(self.lowLimit) == "" and str(self.highLimit == ""):
            outString = "g.cset(g.Julabo01_T_SP, " + str(self.temperature) + ")\n"
        else:
            outString = "g.cset(g.Julabo01_T_SP, " + str(self.temperature) + \
                        " lowLimit=" + str(self.lowLimit) + \
                        " highLimit=" + str(self.highLimit) + ")\n"
        return outString

    def calcTime(self, inst):
        # NEED TO THINJK ABOUT HOW TO ESTIMATE TIME
        return 0

    def makeJSON(self):
        pass

    def toolTip(self):
        pass

#
# class HystLoop(ScriptActionClass.ActionClass):
#     def __init__(self, Sample="", Subtitle="", Angles=[0.7, 2.3], frames=[9000, 27000], fields=[20, 50], measure=[1, 0],
#                  wait="False"):
#         self.Sample = Sample
#         self.Subtitle = Subtitle  #
#         self.Angles = Angles
#         self.Frames = frames
#         self.Fields = fields
#         self.Measure = measure
#         self.wait = wait
#
#     def get_icon(self):
#         return "hystloop1.png"
#
#     def makeAction(self, node):
#         self.Sample = node.child(0, 1).text()
#         self.Subtitle = node.child(1, 1).text()
#
#         tempAngles = node.child(2, 1).text().split(",")
#         self.Angles = [float(a) for a in tempAngles if isfloat(a)]
#
#         tempFrames = node.child(3, 1).text().split(",")
#         self.frames = [float(a) for a in tempFrames if isfloat(a)]
#
#         tempFields = node.child(4, 1).text().split(",")
#         self.Fields = [float(a) for a in tempFields if isfloat(a)]
#
#         tempMeas = node.child(5, 1).text().split(",")
#         self.Measure = [int(a) for a in tempMeas if isint(a)]
#
#         self.wait = node.child(6, 1).text()
#         return self
#
#     def summary(self):
#         degree = str(b'\xc2\xb0', 'utf8')
#         res1 = dict(zip(self.Angles, self.Frames))
#         res = ''.join("({}{}: {}fr) ".format(angle, degree, int(frames)) for angle, frames in res1.items())
#         outString = self.Sample + " " + \
#                     self.Subtitle + \
#                     "\t" + str(res) + \
#                     "fields = [" + ", ".join([str(field) for field in self.Fields]) + "]"
#         return outString
#
#     def isValid(self):
#         if len(self.Angles) != len(self.Frames):
#             return [False, "Number of Angles is not the same as number of frames or empty."]
#         elif any(i > 5 for i in self.Angles):
#             return [False, "One of the angles might be too high."]
#         elif len(self.Angles) == 0:
#             return [False, "Please enter at least on angle/frames pair."]
#         elif len(self.Fields) != len(self.Measure):
#             return [False, "Number of fields is not the same as number of measurements."]
#         else:
#             return [True, "All good!"]
#
#     def stringLine(self, sampleNumber):
#         outString = "\t##### Sample " + str(sampleNumber) + " hysteresis loop\n"
#         outString += "\tfields = [" + ", ".join([str(field) for field in self.Fields]) + "]\n"
#         outString += "\tmeasure = [" + ", ".join([str(meas) for meas in self.Measure]) + "]\n"
#         outString += "\tfor field, meas in zip(fields, measure):\n"
#         outString += "\t\tsample_" + self.Sample + ".subtitle = \"" + self.Subtitle + " field=\" + field\n"
#
#         outString += "\t\tif meas:\n"
#         for a in range(len(self.Angles)):
#             outString +="\t\t\trun_angle(sample_" + self.Sample + ", angle=" \
#                          + str(self.Angles[a]) + ", count_frames=" + str(self.frames[a]) + ", mode=\"PNR\")\n"
#
#         # Change the field:
#         outString += "\t\tg.cset(b.FIELD=field)\n"
#
#         return outString
#
#     def makeJSON(self):
#         rdict = {"RunAngles": [{"label": "Sample", "value": str(self.Sample)}, \
#                                {"label": "Subtitle", "value": str(self.Subtitle)}, \
#                                {"label": "Angles", "value": ['{:.1f}'.format(x) for x in self.Angles]}, \
#                                {"label": "uAmps", "value": ['{}'.format(x) for x in self.uAmps]}]}
#         return json.dumps(rdict, indent=4)
#
#     def calcTime(self, inst):
#         if inst.upper() in ["INTER", "POLREF", "OFFSPEC"]:
#             return (sum(self.frames) / 36000.0 * 60) * self.Measure.count(1)
#         else:
#             return sum(self.frames) / 180.0 * 60
#
#     def toolTip(self):
#         return "Number of Angles and uAmps entries need to be the same."
#

class IterRegistry(type):
    def __iter__(cls):
        return iter(cls._registry)
    
        
class NRsample(object):
    __metaclass__ = IterRegistry
    _registry = []
    
    def __init__(self, row=[]):
        self._registry.append(self)
        
        self.title = 'Title' #row[0]
        self.translation = 'trans' #row[1]
        self.height = 'height' #row[2]
        self.phi_offset = 'phi_offset' #row[3]
        self.psi = 'psi' #row[4]
        self.footprint = 'footprint' #row[5]
        self.resolution = 'resolution' #row[6]
        self.coarse_noMirror = 'coarse_noMirror' #row[7]
        self.switch_pos = 'switch_pos' #row[8]
        #sampleNumber += 1
        
    #sampleNumber=0


if __name__ == '__main__':
    print('This is the NR actions module.\n\nDefined actions are: ')
    actions = [cls.__name__ for cls in ScriptActionClass.ActionClass.__subclasses__()]
    print(actions)