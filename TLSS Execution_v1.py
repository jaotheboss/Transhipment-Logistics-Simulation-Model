"""
This module is outdated as of 16 March 2020. 
This execution file has been replaced by:
- TLSS Execution.py

The simulation module has also been replaced by and split into:
- TransLogShiftingSimulation.py (Simulation)
- SimulationDataCleaner.py (Cleaning)

Action: Shift to Archive
"""

# importing module for simulation
import TuasShiftingSimulation as tss

# importing dataset
import pandas as pd
data = pd.read_excel('cleaned_data.xlsx') # cleaned file for extracting scene data
data_scenario_c = tss.extract_scene_data(data, scenario = 'c')

obs_to_run = 1000
obs_to_bl = 100
obs_to_init = 250

# to start the simulation 
tss.simulate_shifting(data_scenario_c[:obs_to_run], obs_to_run, obs_to_bl, obs_to_init)

# variables for changing
tss.change_variable(17, 'threshold_connectingtime') # default = 12
tss.change_variable(54, 'threshold_back_log') # default = 58
tss.change_variable(58, 'threshold_dd') # default = 55
tss.change_variable(77, 'threshold_dd_empty') # default = 75
tss.change_variable(0.1, 'threshold_transit_to_dest') # default = 0.2
tss.change_variable(10, 'forward_dd') # default = 2
tss.change_variable(10, 'threshold_vehicle_half') # default = 25
tss.change_variable(9, 'move_over') # default = 1

## DIAGNOSTICS
# track the trend for the amount of PMs at each location
x = tss.PMs_track
# check an example of what each PM takes log of 
x = tss.PMs['PM_22'].work_log
x = tss.container

# plots
tss.plot()
