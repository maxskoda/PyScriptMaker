### This script was generated on 04/11/2023, at 17:34:47
### with ScriptMaker (c) Maximilian Skoda 2020 
### Enjoy and use at your own risk. 

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(r"C:\\", "Instrument", "scripts")))
from genie_python import genie as g
from technique.reflectometry import SampleGenerator, run_angle, contrast_change, transmission


def runscript(dry_run=False):
	sample_generator = SampleGenerator(
		    translation = 400.0,
		 height2_offset = 0.0,
		     phi_offset = 0.0,
		     psi_offset = 0.0,
		  height_offset = 0.0,
		     resolution = 0.03,
		      footprint = 60,
		          valve = 1)

	sample_1 = sample_generator.new_sample(title="S1",
		   translation = 100,
		 height_offset = 1,
		    phi_offset = 1,
		    psi_offset = 1,
		     footprint = 1,
		    resolution = 1,
		height2_offset = 1,
		         valve = 1)

	sample_2 = sample_generator.new_sample(title="S2",
		   translation = 200,
		 height_offset = 2,
		    phi_offset = 2,
		    psi_offset = 2,
		     footprint = 2,
		    resolution = 2,
		height2_offset = 2,
		         valve = 2)

	sample_3 = sample_generator.new_sample(title="S3",
		   translation = 300,
		 height_offset = 3,
		    phi_offset = 3,
		    psi_offset = 3,
		     footprint = 3,
		    resolution = 3,
		height2_offset = 3,
		         valve = 3)

	sample_4 = sample_generator.new_sample(title="S4",
		   translation = 400,
		 height_offset = 4,
		    phi_offset = 4,
		    psi_offset = 4,
		     footprint = 4,
		    resolution = 4,
		height2_offset = 4,
		         valve = 4)

	D2O = [100, 0, 0, 0]
	H2O = [0, 100, 0, 0]
	SMW = [38, 62, 0, 0]
	

	##### Sample 1
	sample_1.subtitle="D2O"
	run_angle(sample_1, 0.7, count_uamps=5.0)
	run_angle(sample_1, 2.3, count_uamps=20.0)

	inject(sample_1, H2O, flow=1.5, volume=15.0)

	##### Sample 2
	sample_2.subtitle="D2O"
	run_angle(sample_2, 0.7, count_uamps=5.0)
	run_angle(sample_2, 2.3, count_uamps=20.0)

	inject(sample_2, H2O, flow=1.5, volume=15.0)

	##### Sample 3
	sample_3.subtitle="D2O"
	run_angle(sample_3, 0.7, count_uamps=5.0)
	run_angle(sample_3, 2.3, count_uamps=20.0)

	inject(sample_3, H2O, flow=1.5, volume=15.0)

	##### Sample 4
	sample_4.subtitle="D2O"
	run_angle(sample_4, 0.7, count_uamps=5.0)
	run_angle(sample_4, 2.3, count_uamps=20.0)

	inject(sample_4, H2O, flow=1.5, volume=15.0)

	##### Sample 1
	sample_1.subtitle="H2O"
	run_angle(sample_1, 0.7, count_uamps=15.0)
	run_angle(sample_1, 2.3, count_uamps=20.0)

	##### Sample 2
	sample_2.subtitle="H2O"
	run_angle(sample_2, 0.7, count_uamps=15.0)
	run_angle(sample_2, 2.3, count_uamps=20.0)

	##### Sample 3
	sample_3.subtitle="H2O"
	run_angle(sample_3, 0.7, count_uamps=15.0)
	run_angle(sample_3, 2.3, count_uamps=20.0)

	##### Sample 4
	sample_4.subtitle="H2O"
	run_angle(sample_4, 0.7, count_uamps=15.0)
	run_angle(sample_4, 2.3, count_uamps=20.0)

	go_to_area(600.0, 15.0)

	go_to_pressure(20.0, 15.0)

