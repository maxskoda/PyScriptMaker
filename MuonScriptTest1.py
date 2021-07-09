### This script was generated on 08/07/2021, at 22:21:50
### with ScriptMaker (c) Maximilian Skoda 2020 
### Enjoy and use at your own risk. 

from genie_python.genie_script_generator import ScriptDefinition, cast_parameters_to
from genie_python import genie as g
import numpy as np
from enum import Enum
class SetDefinition(Enum):
...

def magnet_device_type(magnet_device):
...
class DoRun(ScriptDefinition):

def runsscript():
	script_definition = DoRun()
	script_definition.run(**{'start_temperature': keep, 'magnet_device': N/A, 'custom': None, 'start_field': keep, 'mevents': 10, 'stop_field': keep, 'step_field': 0, 'step_temperature': 0, 'stop_temperature': keep})
	script_definition.run(**{'start_temperature': 25, 'magnet_device': N/A, 'custom': None, 'start_field': keep, 'mevents': 10, 'stop_field': keep, 'step_field': 0, 'step_temperature': 5, 'stop_temperature': 55})
