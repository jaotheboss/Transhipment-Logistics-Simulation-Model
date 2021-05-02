"""
This file is to replace the original `TLSS Execution.py` file.
This file is used to execute the simulation model that is based off the other 2 modules.
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 15:17:37 2020

@author: jaoming
"""

import time
from os import chdir
import pandas as pd
chdir('path')

# importing cleaner and simulation module
from SimulationDataCleaner import SimulationDataCleaner
import Class_TuasShiftingSimulation_copy as ctss

# cleaning and extracting of data
from_start = False # if we want to start from a raw file

if from_start:
    # if we're using the module to clean the data from scratch
    data = pd.read_excel('DATA_20200109_sent.xlsx') # raw file
    sdcleaner = SimulationDataCleaner(data)
    sdcleaner.clean()
else:
    # extract a scene from data that is already clean
    clean_data = pd.read_excel('cleaned_data.xlsx') # cleaned file for extracting scene data
    sdcleaner = SimulationDataCleaner(clean_data) 
data_scenario_c = sdcleaner.extract_scene_data('c')

# create an instance of the simulation class (recreate the instance to re-initialize the parameters and the PMs)
## make changes to the parameters here. this will affect the simulation
simulation = ctss.Simulation(tuas_vehicles = 150,
                            city_vehicles = 150,
                            threshold_connectingtime = 12,
                            threshold_back_log = 200,
                            threshold_dd = 55,
                            threshold_dd_empty = 75,
                            threshold_empty_movement = 2,
                            forward_dd = 2,
                            threshold_vehicle_half = 25,
                            move_over = 10)

## make changes to the number of observations you want to run, how many observations you want as back log and how many observations you want to use for initiation
## note: leave head_space as 0 for now
obs_to_run = 100000
head_space = 0
obs_to_bl = 5000
obs_to_init = 500

# start the simulation
start_time = time.time()
simulation.simulate_shifting(data_scenario_c[:obs_to_run],
                            obs_to_run,
                            head_space,
                            obs_to_bl,
                            obs_to_init)
end_time = time.time() - start_time
end_time_seconds = int((end_time % 60)*10)/10
end_time_minutes = int((end_time // 60) % 60)
end_time_hours =  int((end_time // 60) // 60)
print("\nDuration of Simulation:", end_time_hours, 'hours', end_time_minutes, 'minutes', end_time_seconds, 'seconds')
