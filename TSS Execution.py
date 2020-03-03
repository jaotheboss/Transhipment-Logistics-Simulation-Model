import TuasShiftingSimulation as tss

from pandas import read_excel
data = read_excel('tuas_simulation.xlsx')
data_scenario_c = tss.extract_scene_data(data, scenario = 'c')

obs_to_run = 10000   # observations to run
obs_to_bl = 100      # observations to back log
obs_to_init = 200    # observations to initialise 

# execution of the simulation
tss.simulate_shifting(data_scenario_c, obs_to_run, obs_to_bl, obs_to_init)

# for resetting the variables
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


## DIAGNOSTICS
# these are the variables to check
x = tss.PMs_track
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

# plot the evaluation
plot()
       
