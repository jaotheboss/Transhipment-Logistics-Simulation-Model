# Transhipment-Simulation-Model
Simulation Model of transhipment movement of containers between 2 gateways based on certain parameters and discharge timings. 

This project was done during my internship with PSA, with the objective of this simulation being:
    
    1. To observe how many Prime Movers would be needed for the opening of a new port
    
    2. Optimise the kinds of services at each port
    
    3. Observe the activity of each/all Prime Movers based on particular settings/parameters
    
Note:

- Everything here was coded with Python and solely by myself. 

- The dataset used by this simulation cannot be provided.

## Updates:

- The original files `TSS Execution.py` and `TuasShiftingSimulation.py` has been replaced by `Class_TSS Execution.py` and, `Class_TuasShiftingSimulation.py` and `SimulationDataCleaner.py` respectively. 
- The execution file has been streamlined and updated to be based off the 2 new modules that were updated/created for the simulation.
- The 2 new modules are split from the original file for better organisation. The `SimulationDataCleaner.py` file is used solely to clean raw files for the dataset to work with the `Class_TuasShiftingSimulation.py` simulation module.
- The `Class_TuasShiftingSimulation.py` has been updated and organized into classes instead of separate functions for all. This is for easy readability for next few users. 

**In the Works**

1. Machine Learning Model to determine the optimal parameters
    
2. Further improvement in the visualisations of the Simulation Model and the upcoming Machine Learning Model
