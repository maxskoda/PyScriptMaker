class run_angle_polref(ScriptActionClass.ActionClass):
    def __init__(self, sample_stack="", angles=[0.5, 1.6], Subtitle="",
                 frames=[36000, 36000], number_of_runs=[1, 4], pol_mode='PNR'):
        self.Sample = sample_stack  # model.item(row).child(0,1).text()
        self.Subtitle = Subtitle  # model.item(row).child(1,1).text()
        self.angles = angles  # model.item(row).child(2,1).text()
        self.frames = frames  # model.item(row).child(3,1).text()
        self.runs = number_of_runs
        self.pol_mode = pol_mode

    def makeAction(self, node):
        self.Sample = node.child(0, 1).text()
        self.Subtitle = node.child(1, 1).text()

        tempAngles = node.child(2, 1).text().split(",")
        self.angles = [float(a) for a in tempAngles if isfloat(a)]

        temp_frames = node.child(3, 1).text().split(",")
        self.frames = [float(a) for a in temp_frames if isfloat(a)]

        self.runs = node.child(4, 1).text()
        return self

    def summary(self):
        degree = str(b'\xc2\xb0', 'utf8')
        res1 = dict(zip(self.angles, self.frames))
        res = ''.join("({}{}: {}frames) ".format(angle, degree, int(frames)) for angle, frames in res1.items())
        outString = self.Sample + " " + \
                    self.Subtitle + \
                    "\t" + str(res)
        return outString

    def isValid(self):
        if len(self.angles) != len(self.frames):
            return [False, "Number of Angles is not the same as number of uAmps or empty."]
        elif any(i > 5 for i in self.angles):
            return [False, "One of the angles might be too high."]
        elif len(self.angles) == 0:
            return [False, "Please enter at least on angle/uAmp pair."]
        else:
            return [True, "All good!"]

    def stringLine(self, sampleNumber):
        outString = "##### Sample " + str(sampleNumber) + "\n"
        outString += "angles = " + str(self.angles) + "\n"
        outString += "frames = " + str(self.frames) + "\n"
        outString += "runs = [" + str(self.runs) + "]\n"
        outString += "for angle, frame, run_no in zip(angles, frames, runs):\n"
        outString += "\tinst.run_angle_polref(angle=angle, number_of_runs=run_no,\n"
        outString += "\t\t\t\t\t\trun_frames=frame, run_name="+self.Subtitle+")\n"
        outString += "\t\t\t\t\t\tsample_stack=sample, pol_mode=" + self.pol_mode + ")\n"

        return outString

    def makeJSON(self):
        rdict = {"RunAngles": [{"label": "Sample", "value": str(self.Sample)}, \
                               {"label": "Subtitle", "value": str(self.Subtitle)}, \
                               {"label": "Angles", "value": ['{:.1f}'.format(x) for x in self.angles]}, \
                               {"label": "frames", "value": ['{}'.format(x) for x in self.frames]}]}
        return json.dumps(rdict, indent=4)

    def calcTime(self, inst):
        if inst in ["INTER", "POLREF", "OFFSPEC"]:
            return sum(self.uAmps) / 40.0 * 60
        else:
            return sum(self.uAmps) / 180.0 * 60

    def toolTip(self):
        return "Number of Angles and uAmps entries need to be the same."


class SampleLoop(ScriptActionClass.ActionClass):
    def __init__(self, samples=[], Subtitle="", Angles=[0.7, 2.3], uAmps=[5, 20], contrastChange_to="H2O"):
        self.samples = [samples] # model.item(row).child(0,1).text()
        self.Subtitle = Subtitle  # model.item(row).child(1,1).text()
        self.Angles = Angles  # model.item(row).child(2,1).text()
        self.uAmps = uAmps  # model.item(row).child(3,1).text()
        self.contrast_change = contrastChange_to

    def makeAction(self, node):
        self.Sample = node.child(0, 1).text()
        self.Subtitle = node.child(1, 1).text()

        tempAngles = node.child(2, 1).text().split(",")
        self.Angles = [float(a) for a in tempAngles if isfloat(a)]

        tempAmps = node.child(3, 1).text().split(",")
        self.uAmps = [float(a) for a in tempAmps if isfloat(a)]

        self.contrast_change = node.child(4, 1).text()
        return self

    def summary(self):
        degree = str(b'\xc2\xb0', 'utf8')
        res1 = dict(zip(self.Angles, self.uAmps))
        res = ''.join("({}{}: {}\u03BCA) ".format(angle, degree, int(uamps)) for angle, uamps in res1.items())
        outString = self.Sample + " " + \
                    self.Subtitle + \
                    "\t" + str(res) +\
                    "->" + self.contrast_change
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
        outString = "LOOP ii FROM 1 TO " + str(len(self.samples)) + "\n"
        # outString = "##### Sample " + str(sampleNumber) + "\n"
        outString += "sample[ii].subtitle = \"" + self.Subtitle + "\"\n"

        for a in range(len(self.Angles)):
            outString += "runTime = runAngles(sample[ii]," + str(self.Angles[a]) + "," + str(
                self.uAmps[a]) + ")\n"
        return outString

    def makeJSON(self):
        rdict = {"RunAngles": [{"label": "Sample", "value": str(self.Sample)}, \
                               {"label": "Subtitle", "value": str(self.Subtitle)}, \
                               {"label": "Angles", "value": ['{:.1f}'.format(x) for x in self.Angles]}, \
                               {"label": "uAmps", "value": ['{}'.format(x) for x in self.uAmps]}]}
        return json.dumps(rdict, indent=4)

    def calcTime(self, inst):
        if inst in ["INTER", "POLREF", "OFFSPEC"]:
            return sum(self.uAmps) / 40.0 * 60
        else:
            return sum(self.uAmps) / 180.0 * 60

    def toolTip(self):
        return "Number of Angles and uAmps entries need to be the same."