### This script was generated on 13/02/2022, at 00:06:21
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

	sample_1 = sample_generator.new_sample(title="S1 Si PyAu COOH-OEG-SAM",
		   translation = 37,
		 height_offset = -2.09,
		    phi_offset = 0.35-0.3498,
		    psi_offset = -0.2,
		     footprint = 60,
		    resolution = 0.035,
		height2_offset = 0,
		         valve = 1)

	sample_2 = sample_generator.new_sample(title="S2 Si PyAu COOH-OEG-SAM",
		   translation = 214,
		 height_offset = -2.555,
		    phi_offset = -0.094-0.3476,
		    psi_offset = 0.0,
		     footprint = 60,
		    resolution = 0.035,
		height2_offset = 0,
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

	D2O = [100, 0, 0, 0]
	H2O = [0, 100, 0, 0]
	SMW = [38, 62, 0, 0]
	AuMW = [75, 25, 0, 0]
	

	##### Sample 1
	sample_1.subtitle="BamABCDE 8:2 POPC POPS + dOmpT SurA Inc H2O"
	run_angle(sample_1, 0.35, count_uamps=40.0)
	run_angle(sample_1, 0.65, count_uamps=60.0)
	run_angle(sample_1, 1.5, count_uamps=130.0)

	contrast_change(sample_1.valve, H2O, 1.5, 15.0, wait=True)

	##### Sample 1
	sample_1.subtitle="BamABCDE 8:2 POPC POPS + dOmpT SurA Inc H2O flush"
	run_angle(sample_1, 0.35, count_uamps=40.0)
	run_angle(sample_1, 0.65, count_uamps=60.0)
	run_angle(sample_1, 1.5, count_uamps=130.0)

	contrast_change(sample_1.valve, D2O, 1.5, 15.0, wait=True)

	##### Sample 1
	sample_1.subtitle="BamABCDE 8:2 POPC POPS + dOmpT SurA Inc D2O flush"
	run_angle(sample_1, 0.3, count_uamps=40.0)
	run_angle(sample_1, 0.7, count_uamps=60.0)
	run_angle(sample_1, 1.5, count_uamps=130.0)

	contrast_change(sample_1.valve, AuMW, 1.5, 15.0, wait=True)

	##### Sample 1
	sample_1.subtitle="BamABCDE 8:2 POPC POPS + dOmpT SurA Inc AuMW flush"
	run_angle(sample_1, 0.3, count_uamps=40.0)
	run_angle(sample_1, 0.7, count_uamps=60.0)
	run_angle(sample_1, 1.5, count_uamps=130.0)

	contrast_change(sample_1.valve, SMW, 1.5, 15.0, wait=True)

	##### Sample 1
	sample_1.subtitle="BamABCDE 8:2 POPC POPS + dOmpT SurA Inc SMW flush"
	run_angle(sample_1, 0.3, count_uamps=40.0)
	run_angle(sample_1, 0.7, count_uamps=60.0)
	run_angle(sample_1, 1.5, count_uamps=130.0)

