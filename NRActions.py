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
                "FORWARD experimentsettings\n\n" + \
                "PROCEDURE runscript\n"+\
                "GLOBAL runtime\n"+\
                "LOCAL ii\n\n"+\
                "CHANGE NPERIODS=1\n"+\
                "cset monitor 1\n"+\
                "experimentsettings\n"+\
                "#====================================\n"+\
                "#These should be changed with each sample change:\n"+\
                "#====================================\n"
    sampList=[]            
    for samp in range(len(samples)):
        outString += "          sample[" + str(samp+1) + "].title = \"" + samples[samp].get("Sample/Title") +"\"\n"+\
                     "    sample[" + str(samp+1) + "].translation = " + samples[samp].get("Trans") +"\n"+\
                     "         sample[" + str(samp+1) + "].height = " + samples[samp].get("Height") +"\n"+\
                     "     sample[" + str(samp+1) + "].phi_offset = " + samples[samp].get("Phi Offset") +"\n"+\
                     "            sample[" + str(samp+1) + "].psi = " + samples[samp].get("Psi") + "\n"+\
                     "#====================================\n"
                     #"      s" + str(samp+1) + ".footprint = " + samples[samp].get("Footprint") +"\n"+\
                     #"     s" + str(samp+1) + ".resolution = " + samples[samp].get("Resolution") +"\n"+\
                     #"s" + str(samp+1) + ".coarse_nomirror = " + samples[samp].get("Coarse_noMirror") +"\n"+\                                        
                     #"       s" + str(samp+1) + ".subtitle = \"\""  +"\n"+\
                     
    outString += "#====================================\n\n"+\
                 "#====================================\n"+\
                 "#Script body begins here:\n"+\
                 "#====================================\n\n"
    return outString

def writeFooter(samples):
    ## for OpenGenie
    outString = "ENDPROCEDURE\n\n" + \
                "PROCEDURE experimentsettings\n"+\
                "GLOBAL S1 S2 S3 S4 S5 S6 S7 sample\n"+\
                "#====================================\n"+\
                "#Generic settings for all samples which do not need to be changed during experiment:\n"+\
                "#====================================\n"+\
                "s1=fields(); s2=fields(); s3=fields(); s4=fields(); s5=fields(); s6=fields(); s7=fields()\n"+\
                "#====================================\n"
    for samp in range(len(samples)):
        outString += "     s" + str(samp+1) + ".phi_offset = " + samples[samp].get("Phi Offset") +"\n"+\
                     "            s" + str(samp+1) + ".psi = " + samples[samp].get("Psi") + "\n"+\
                     "      s" + str(samp+1) + ".footprint = " + samples[samp].get("Footprint") +"\n"+\
                     "     s" + str(samp+1) + ".resolution = " + samples[samp].get("Resolution") +"\n"+\
                     "s" + str(samp+1) + ".coarse_nomirror = " + samples[samp].get("Coarse_noMirror") +"\n"+\
                     "         s" + str(samp+1) + ".height = " + samples[samp].get("Height") +"\n"+\
                     "          s" + str(samp+1) + ".title = \"" + samples[samp].get("Sample/Title") +"\"\n"+\
                     "       s" + str(samp+1) + ".subtitle = \"\""  +"\n"+\
                     "    s" + str(samp+1) + ".translation = " + samples[samp].get("Trans") +"\n"+\
                     "#====================================\n"
    outString += "sample=dimensions(7)\n" +\
                 "sample[1]=s1; sample[2]=s2; sample[3]=s3; sample[4]=s4; sample[5]=s5; sample[6]=s6; sample[7]=s7\n"

    outString += "ENDPROCEDURE\n"                                
    return outString

class RunAngles(ScriptActionClass.ActionClass):
    def __init__(self, Sample="", Subtitle="", Angles=[0.7, 2.3], uAmps=[5, 20]):
        self.Sample = Sample #model.item(row).child(0,1).text()
        self.Subtitle = Subtitle #model.item(row).child(1,1).text()
        self.Angles = Angles #model.item(row).child(2,1).text()
        self.uAmps = uAmps #model.item(row).child(3,1).text()

    def makeAction(self, node):
        self.Sample = node.child(0, 1).text()
        self.Subtitle = node.child(1, 1).text()

        tempAngles = node.child(2, 1).text().split(",")
        self.Angles = [float(a) for a in tempAngles if isfloat(a)]


        tempAmps = node.child(3, 1).text().split(",")
        self.uAmps = [float(a) for a in tempAmps if isfloat(a)]
        return self

    def summary(self):
        res = dict(zip(self.Angles, self.uAmps))
        outString = self.Sample + " " +\
                    self.Subtitle +\
                    "\t" + str(res)
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
        outString = "##### Sample " + str(sampleNumber) + "\n"
        outString += "sample[" + str(sampleNumber) + "].subtitle = \"" + self.Subtitle + "\"\n"
        
        for a in range(len(self.Angles)):
            outString += "runTime = runAngles(sample[" + str(sampleNumber) + "]," + str(self.Angles[a]) + "," + str(self.uAmps[a]) + ")\n"
        return outString
    
    def makeJSON(self):
        rdict = {"RunAngles": [{ "label": "Sample", "value": str(self.Sample) },\
                       { "label": "Subtitle", "value": str(self.Subtitle) },\
                       { "label": "Angles", "value": ['{:.1f}'.format(x) for x in self.Angles]},\
                       { "label": "uAmps", "value": ['{}'.format(x) for x in self.uAmps]}]}
        return json.dumps(rdict, indent=4)

    def calcTime(self, inst):
        if inst in ["INTER", "POLREF", "OFFSPEC"]:
            return sum(self.uAmps) / 40.0 * 60
        else:
            return sum(self.uAmps) / 180.0 * 60

    def toolTip(self):
        return "Number of Angles and uAmps entries need to be the same."

class Inject(ScriptActionClass.ActionClass):
    def __init__(self, Sample="", Solution="D2O", Flow=1.5, Volume=15.0):
        self.Sample = Sample #model.item(row).child(0,1).text()
        self.solution = Solution
        self.flow = tofloat(Flow)
        self.volume = tofloat(Volume)
        
    def makeAction(self, node):
        self.Sample = node.child(0, 1).text()
        self.solution = node.child(1, 1).text()
        self.flow = tofloat(node.child(2, 1).text())
        self.volume = tofloat(node.child(3, 1).text())
        return self

    def isValid(self):
        if str(self.solution).upper() in \
                ["D2O", "H2O", "SMW", "SiCM", "SYRINGE_A", "SYRINGE_B"]:
            return [True, "All good!"]
        else:
            return [False, "Requested liquid not valid. Must be D2O, H2O, SMW, SiCM, SYRINGE_A, SYRINGE_B"]
        
    def summary(self):
        return '{}, {}, {}, {}'.format(self.Sample, self.solution, self.flow, self.volume)
        
    def stringLine(self, sampleNumber):
        outString = "runTime = inject(" + str(sampleNumber) + ", \"" + self.solution + \
                        "\"," + str(self.flow) + "," + str(self.volume) + ")\n"
        return outString
    
    def makeJSON(self):
        rdict = {"Inject": [{ "label": "Sample", "value": str(self.Sample) },\
                   { "label": "Solution", "value": str(self.solution)},\
                   { "label": "Flow", "value": str(self.flow)},\
                   { "label": "Volume", "value": str(self.volume)}]
            }
        return json.dumps(rdict, indent=4)

    def calcTime(self, inst):
        return 0 ### needts to change if "wait" implemented

    def toolTip(self):
        return "Valid input: D2O, H2O, SMW, SiCM, SYRINGE_A, SYRINGE_B. HPLC: A - D2O, B - H2O"

class ContrastChange(ScriptActionClass.ActionClass):
    def __init__(self, Sample="", concA=100, concB=0, concC=0, concD=0, Flow=1.0, Volume=10.0):
        self.Sample = Sample #model.item(row).child(0,1).text()
        self.concA = concA
        self.concB = concB
        self.concC = concC
        self.concD = concD
        self.flow = Flow
        self.volume = Volume
        
    def makeAction(self, node):
        self.Sample = node.child(0,1).text()
        self.concA = node.child(1,1).text()
        self.concB = node.child(2,1).text()
        self.concC = node.child(3,1).text()
        self.concD = node.child(4,1).text()
        self.flow = node.child(5,1).text()
        self.volume = node.child(6,1).text()        
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
        return '{}, {}, {}, {}, {}, {}, {}'.format(self.Sample, self.concA, self.concB, self.concC, self.concD, self.flow, self.volume)
        
    def stringLine(self, sampleNumber):
        outString = "runTime = contrastChange(" + str(sampleNumber) + "," + self.concA + "," + self.concB + "," + self.concC + "," + self.concD + \
                        "," + self.flow + "," + self.volume + ")\n"
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
        return 0 ### needts to change if "wait" implemented

    def toolTip(self):
        return "Concentrations in % and need to add up to 100."

class Transmission(ScriptActionClass.ActionClass):
    def __init__(self, s1vg=1.0 ,s2vg=0.5, s1hg=50, s2hg=30, Sample="", Subtitle="", uAmps=20, s4hg=53.0, height_offset=5, sm_angle=0.75):
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
            print(attr)
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
        outString = "runTime = transmission(sample[" + str(sampleNumber) + "], \"" + self.Subtitle + "\", " + str(self.uAmps) + "," + str(self.s1vg) + "," + str(self.s2vg) +\
                                                "," + str(self.s1hg) + "," + str(self.s2hg) + "," + str(self.s4hg)
        if str(self.height_offset) != "":
            outString += "," + str(self.height_offset)
        if str(self.sm_angle) != "":
            outString += "," + str(self.sm_angle)
                                                
        return outString+")\n"

    def calcTime(self, inst):
        if inst in ["INTER", "POLREF", "OFFSPEC"]:
            return self.uAmps / 40.0 * 60
        else:
            return self.uAmps / 180.0 * 60

    def toolTip(self):
        pass
 
class GoToPressure(ScriptActionClass.ActionClass):
    def __init__(self, pressure=20.0, speed=15.0):
        # self.Sample = "" # dummy
        self.pressure = pressure
        self.speed = speed # [cm^2/min]

        
    def makeAction(self, node):
        # self.Sample = node.child(0, 1).text()
        self.pressure = node.child(0, 1).text()
        self.speed = node.child(1, 1).text()
        return self

    def isValid(self):
        return [True]
        
    def summary(self):
        return 'p={} mN,  speed={} cm^2/min'.format(self.pressure, self.speed)
        
    def stringLine(self, sampleNumber):
        outString = "runTime = goToPressure(" + str(self.pressure) + ", " + str(self.speed) + ")\n"
        return outString

    def calcTime(self, inst):
        # NEED TO THINK ABOUT HOW TO ESTIMATE TIME!!!!
        return 0

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
            outString = "cset/nocontrol Julabo_WB = " + str(self.temperature) + "\n"
        else:
            outString = "cset/control Julabo_WB = " + str(self.temperature) + \
                        " lowLimit=" + str(self.lowLimit) + \
                        " highLimit=" + str(self.highLimit) + "\n"
        return outString

    def calcTime(self, inst):
        # NEED TO THINJK ABOUT HOW TO ESTIMATE TIME
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
        #sampleNumber += 1
        
    #sampleNumber=0


if __name__ == '__main__':
    print('This is the NR actions module.\n\nDefined actions are: ')
    actions = [cls.__name__ for cls in ScriptActionClass.ActionClass.__subclasses__()]
    print(actions)