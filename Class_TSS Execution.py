"""
This file is to replace the original `TSS Execution.py` file.
This file is used to execute the simulation model that is based off the other 2 modules.
"""
from os import chdir
chdir('*change to the directory with the dataset and modules*')

# importing dataset
import pandas as pd

from SimulationDataCleaner import SimulationDataCleaner # module number 1
## if we're using the module to clean the data from scratch
# data = pd.read_excel('DATA_20200109_sent.xlsx')
# sdcleaner = SimulationDataCleaner(data)
# sdcleaner.clean()
# data_scenario_c = sdcleaner.extract_scene_data('c')

# if we're using the module to extract a scene from data that is already clean
clean_data = pd.read_excel('cleaned_data.xlsx') # cleaned file for extracting scene data
sdcleaner = SimulationDataCleaner(clean_data)
data_scenario_c = sdcleaner.extract_scene_data('c')

# importing module for simulation
import Class_TuasShiftingSimulation as ctss # module number 2

# create an instance of the simulation class (recreate the instance to re-initialize the parameters and the PMs)
simulation = ctss.Simulation(tuas_vehicles = 150,
                             city_vehicles = 150,
                             threshold_connectingtime = 12,
                             threshold_back_log = 58,
                             threshold_dd = 55,
                             threshold_dd_empty = 75,
                             threshold_transit_to_dest = 0.2,
                             forward_dd = 2,
                             threshold_vehicle_half = 25,
                             move_over = 1)

obs_to_run = 2500
obs_to_bl = 250
obs_to_init = 375

# start the simulation
simulation.simulate_shifting(data_scenario_c,
                             obs_to_run,
                             obs_to_bl,
                             obs_to_init)


## DIAGNOSTICS
# track the trend for the amount of PMs at each location
x = simulation.PMs_track
# check an example of what each PM takes log of 
x = simulation.PMs['PM_22'].work_log
x = simulation.container
