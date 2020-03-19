# Transhipment-Simulation-Model
Simulation Model of transhipment movement of containers between 2 gateways based on certain parameters and discharge timings. 

This project was done during my internship with PSA, with the objective of this simulation being:
    
    1. To observe how many Prime Movers would be needed for the opening of a new port
    
    2. Optimise the kinds of services at each port
    
    3. Observe the activity of each/all Prime Movers based on particular settings/parameters
    
Note:

- Everything here was coded with Python and solely by myself. 

- The dataset used by this simulation cannot be provided.

## Updates [CAA]:

#### [19/03/2020]
- 72.7% improvement in time complexity

- Fixed a bug where the N2 containers were not being tracked properly; given the situation that they have been tagged N2 but there're no available PMs, and therefore their turn to be moved is skipped indefinitely

- Updated the logic for sending off empty PMs over to either sides

#### [16/03/2020]
- The original files `TSS Execution.py` and `TuasShiftingSimulation.py` has been replaced by `Class_TSS Execution.py` and, `Class_TuasShiftingSimulation.py` and `SimulationDataCleaner.py` respectively. 

- The execution file has been streamlined and updated to be based off the 2 new modules that were updated/created for the simulation.

- The 2 new modules are split from the original file for better organisation. The `SimulationDataCleaner.py` file is used solely to clean raw files for the dataset to work with the `Class_TuasShiftingSimulation.py` simulation module.

- The `Class_TuasShiftingSimulation.py` has been updated and organized into classes instead of separate functions for all. This is for easy readability for next few users. 

#### [12/03/2020]
- Speed increase by 10%

- Updated plots and prints such that each simulation would eventually:
    - Export discharge and arrival timings
    - Export all image diagnostics
    - Export all text diagnostics

**In the Works**

1. Machine Learning Model to determine the optimal parameters
    
2. Further improvement in the visualisations of the Simulation Model and the upcoming Machine Learning Model

#### Tips and Tricks I've Learnt for Speed Optimisation:
1. Using numpy for vectorized functions are really quick
2. For pandas dataframe, using `df.iat[x, y]` for extracting a single value is much faster
3. Randomisation can be slow, the fastest one would be `np.random.rand()`, although the values are between 0 and 1
4. Rounding can be slow too. If you want a value of either 0 or 1, you can `int(np.random.rand() + 0.5)`, since `int()` cuts the float
5. List comprehensions are always much faster than using `filter` or `map`. Although `filter` and `map` are much faster than using loops
6. Look at all the loops in the program and write lines to stop the loop from running if it's pointless to continue. Basically, add `break` in loops whenever you can
7. Using `enumerate` to find the index is much faster
