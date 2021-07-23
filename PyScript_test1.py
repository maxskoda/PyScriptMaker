### This script was generated on 22/07/2021, at 22:26:39
### with ScriptMaker (c) Maximilian Skoda 2020 
### Enjoy and use at your own risk. 

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(r"C:\\", "Instrument", "scripts")))
from genie_python import genie as g
from technique.reflectometry import SampleGenerator, run_angle, contrast_change, transmission


def runscript(dry_run=False):
	sample_generator = SampleGenerator(
		translation=400.0,
		height2_offset=0,
		phi_offset=0.0,
		psi_offset=0.0,
		height_offset=0.0,
		resolution=0.03,
		footprint=60)

	sample_S1= sample_generator.new_sample(title="S1",
		translation=100,
		height_offset=1,
		phi_offset=1,
		psi_offset=1)

	sample_S2= sample_generator.new_sample(title="S2",
		translation=200,
		height_offset=2,
		phi_offset=2,
		psi_offset=2)

	sample_S3= sample_generator.new_sample(title="S3",
		translation=300,
		height_offset=3,
		phi_offset=3,
		psi_offset=3)

	sample_S4= sample_generator.new_sample(title="S4",
		translation=400,
		height_offset=4,
		phi_offset=4,
		psi_offset=4)

	##### Sample 1
	sample_S1.subtitle="D2O"
	run_angle(sample_S1, angle=0.7, count_uamps=5.0, mode="NR")
	run_angle(sample_S1, angle=2.3, count_uamps=20.0, mode="NR")

	inject(sample_S1, "H2O", 1.5, 15.0)

	##### Sample 2
	sample_S2.subtitle="D2O"
	run_angle(sample_S2, angle=0.7, count_uamps=5.0, mode="NR")
	run_angle(sample_S2, angle=2.3, count_uamps=20.0, mode="NR")

	inject(sample_S2, "H2O", 1.5, 15.0)

	##### Sample 3
	sample_S3.subtitle="D2O"
	run_angle(sample_S3, angle=0.7, count_uamps=5.0, mode="NR")
	run_angle(sample_S3, angle=2.3, count_uamps=20.0, mode="NR")

	inject(sample_S3, "H2O", 1.5, 15.0)

	##### Sample 4
	sample_S4.subtitle="D2O"
	run_angle(sample_S4, angle=0.7, count_uamps=5.0, mode="NR")
	run_angle(sample_S4, angle=2.3, count_uamps=20.0, mode="NR")

	inject(sample_S4, "H2O", 1.5, 15.0)

	##### Sample 1
	sample_S1.subtitle="H2O"
	run_angle(sample_S1, angle=0.7, count_uamps=15.0, mode="NR")
	run_angle(sample_S1, angle=2.3, count_uamps=20.0, mode="NR")

	##### Sample 2
	sample_S2.subtitle="H2O"
	run_angle(sample_S2, angle=0.7, count_uamps=15.0, mode="NR")
	run_angle(sample_S2, angle=2.3, count_uamps=20.0, mode="NR")

	##### Sample 3
	sample_S3.subtitle="H2O"
	run_angle(sample_S3, angle=0.7, count_uamps=15.0, mode="NR")
	run_angle(sample_S3, angle=2.3, count_uamps=20.0, mode="NR")

	##### Sample 4
	sample_S4.subtitle="H2O"
	run_angle(sample_S4, angle=0.7, count_uamps=15.0, mode="NR")
	run_angle(sample_S4, angle=2.3, count_uamps=20.0, mode="NR")

