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
