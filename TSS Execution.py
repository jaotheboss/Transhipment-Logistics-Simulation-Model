# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 14:29:11 2020

@author: atttjmg1
"""
# proportion of time spent for each PM
# proportion of PM on each side for each time slot
from os import chdir
chdir('/Users/jaoming/Desktop/UPIP1920/TSS')

import TuasShiftingSimulation as tss
# cleaned = tss.clean_data(tss.data)

# since data has been cleaned before, we just read the csv file
from pandas import read_excel
data = read_excel('new_data.xlsx')
data_scenario_c = tss.extract_scene_data(data, scenario = 'c')

obs_to_run = 10000
obs_to_bl = 100
obs_to_init = 200

# to start the simulation
tss.simulate_shifting(data_scenario_c, obs_to_run, obs_to_bl, obs_to_init)

tss.reset_variables()
# variables for changing
tss.change_variable(17, 'threshold_connectingtime') # default = 12
tss.change_variable(54, 'threshold_back_log') # default = 58
tss.change_variable(58, 'threshold_dd') # default = 55
tss.change_variable(77, 'threshold_dd_empty') # default = 75
tss.change_variable(0.1, 'threshold_transit_to_dest') # default = 0.2
tss.change_variable(10, 'forward_dd') # default = 2
tss.change_variable(10, 'threshold_vehicle_half') # default = 25
tss.change_variable(9, 'move_over') # default = 1

tss.full_load[0] / sum(tss.full_load + tss.half_load + tss.empty_load)

## DIAGNOSTICS
# track the trend for the amount of PMs at each location
x = tss.PMs_track
# check an example of what each PM takes log of 
x = tss.PMs['PM_22'].work_log
x = tss.container

# evaluation methods
def plot():
       # vehicle location trends
       tss.plot_vehicle_pattern()
       
       # diagnostics for loads that were carried
       tss.plot_varying_loads()
       
       # something
       tss.load_evaluation()
       
       # backlog and demand diagnostics
       tss.plot_dd_back_log()
       
       # how many containers have been moved
       print('\nStatus of Containers (Count):')
       total_containers = len(tss.container['moved_index']) - tss.container['moved_index'].count('init')
       moved_1s = tss.container['moved_index'][:obs_to_run].count(1)
       not_moved_0s = tss.container['moved_index'][:obs_to_run].count(0)
       couldnt_move_n2 = tss.container['moved_index'][:obs_to_run].count('N2')
       print('Moved:    ', moved_1s, '   \t(' + str(round((moved_1s / total_containers)*100, 2)) + '%)')
       print('Untouched:', not_moved_0s, '   \t(' + str(round((not_moved_0s / total_containers)*100, 2)) + '%)')
       print('Missed:   ', couldnt_move_n2, '   \t(' + str(round((couldnt_move_n2 / total_containers)*100, 2)) + '%)')

plot()

"""
Tips to optimizing Python code:
1. Using the Operator.itemgetter() function. It's basically a slicer.
operator.itemgetter(1)([5,2,3,4]) will return 2
operator.itemgetter('key')({'key': 'value'}) will return 'value'

2. Using `map` instead of a loop, because `map`s are built-in constructs
And the python engine takes up substantial efforts in interpreting the loop constructs

3. Using built-in functions in general
- `map`, `enumerate`, `eval`, `filter`, `open`, anything from os module, `

4. Limit Method Lookup
for it in xrange(10000):
       myLib.findMe(it)

instead of the above, we do this -
findMe = myLib.findMe
for it in xrange(10000):
       findMe(it)
"""
       