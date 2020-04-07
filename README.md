# Transhipment-Simulation-Model
Simulation Model of the movement of transhipment logistics from 1 location to another to ascertain its timeliness.

This project was inspired during my internship with PSA, with the objective of this simulation being:
    
    1. To determine the effects of the number of movers with regards to the containers arrival time
    
    2. Understand the activity pattern of each mover
    
    3. Observe the long term impacts of such a system
    
Note:

- Everything here was coded with Python and solely by myself. 

- The dataset used by this simulation cannot be provided.

- There were 2 original files, the model and execution file. However, i've come to realise the how messy things could get and have converted my 2 original files into 3 different kinds of files - Cleaning, Model and Execution

- All 3 of these files, except for the Execution file, are in class form for easier readability. 

- I assume that the 2 locations are Tuas and City, as these are the 2 main ports in Singapore. 

## Description:
The Transhipment Logistics Shifting Simulation model consists of 3 parts - the cleaning, the model and the execution.

### The Cleaning:
The file `SimulationDataCleaner.py` documents all the functions and method used for cleaning the raw data into something    usable for the Simulation model. This file is used as a module in the execution file to clean and organise the data. Its    main methods are: clean() and extract_scene_data(), which can be seen in the execution file.

```
For example,
from SimulationDataCleaner import SimulationDataCleaner        # importing the file in as a module
data = pd.read_excel('DATA_20200109_sent.xlsx')                # reading the raw file
sdcleaner = SimulationDataCleaner(data)                        # the cleaner object is initiated with the raw file
sdcleaner.clean()                                              # this method cleans the file and updates the data it's holding with the cleaned data file
data_scenario_c = sdcleaner.extract_scene_data('c')            # the extraction is done and it both updates the data attrbute of the cleaner object and returns the extracted data
```

For convenience sake, i shall go through the 2 functions here.
clean() = takes in a raw data file and 'cleans' it such that all the scene data is there, and that the dataframe is in the correct shape
extract_scene_data() = takes in the cleaned data file and extracts only the utilized columns, including one of the connection times (based on the scene) that is used for the Simulation

### The Model:
This `TransLogShiftingSimulation.py` file contains the Simulation model itself alongside helper and plotting functions for the evaluation and tracking of the Simulation. 
Similar to the cleaning aspect, this file is meant to be imported into the execution file as a module as well. 

The 2 main classes within this file are the Simulation class and the PM class. The PM class is created as it's fundamental to the way the Simulation works, and holds plenty of tracking information.

The Simulation takes in a few variables that guides the Simulation:
1. tuas_vehicles
2. city_vehicles 
3. threshold_connectingtime 
4. threshold_back_log 
5. threshold_dd 
6. threshold_dd_empty 
7. threshold_empty_movement 
8. forward_dd
9. threshold_vehicle_half 
10. move_over 
All of the variables are explained within the file itself and can be seen in the docstring for the class

### The Execution:
The 'TLSS_Execution.py' file is the culmination of all 3 of the files, where it takes the previous two mentioned files and imports them as modules to use them. 

The execution file is split into 3 main parts: the cleaning, the initiating and the simulation itself. 
These parts are pretty self explanatory. 

The first part are for the cleaning of the dataset. 
At this point, there should be one main dataset that you'd be using to run the Simulation model on. (5 columns and however many observations)

The second part, is the initiation of the Simulation model. Since the model comes from a class, an instance of the Simulation model has to be created.
Hence, the instance of a Simulation model is created alongside all the variables that it is to be initiated with for the Simulation to run. 
On top of that, the number of observations, headspace, backlog and initiation observations that is desired to run will be established as well.

The last and final part, is the execution of the Simulation.
This is done through the simulate_shifting() method within the model module. 
The last section is for the timing and the Simulation itself to start running. 
After the running of the Simulation, things should be returned are:

1. Graphs
2. Text files that explains the graphs
3. Time taken for the Simulation to run

## How to Run the Simulation:
1. Before starting with anything, make sure the raw data file, cleaning file and simulation model file (and cleaned data file if applicable) is in the same folder.

2. Open the Simulation model file ('TransLogShiftingSimulation.py') -> Change the origin variable on line 10 to the work directory of step 1.

3. Open the execution file ('TLSS_Execution.py')

4. Change the string in this line into the directory of the aforementioned folder -> chdir('your directory') # Note: if unsure, import os, use getcwd() to find out what working directory you're in

5. Change `from_start` to True if you want to clean the data from its raw state, else you can leave it as False

6. Change the parameters for the Simulation if you want

7. Change the number of observations that you want to run from the dataset. # Note: each value is independent of each other. eg. 10 observations, 2 backlog and 1 init means, out of the 10 observations, we'll save 2 for backlog and then after that use 1 for init

8. Save the file 
    
    If you're on IDE: 
    Just run it.

    If you're on terminal: 
    Open terminal ->
    Change directory to the aforementioned folder in step 1 ->
    Run code `python TLSS_Execution.py`

## Updates [CAA]:

#### [02/04/2020]
- Shifted around the algorithm for an increase in efficiency. Resulted in a 50% increase in timing.

- Added a timing option such that i wouldn't have to use magic functions in the interactive shell. 

#### [19/03/2020]
- 72.7% improvement in time complexity

- Fixed a bug where the Late containers were not being tracked properly; given the situation that they have been tagged Late but there're no available PMs, and therefore their turn to be moved is skipped indefinitely

- Updated the logic for sending off empty PMs over to either sides

#### [16/03/2020]
- The original file `TransLogShiftingSimulation.py` has been replaced by class versions. This is such that it would be easier to read and track

- The execution file has been streamlined and updated to be based off the 2 new modules that were updated/created for the simulation.

- The 2 new modules are split from the original file for better organisation. The `SimulationDataCleaner.py` file is used solely to clean raw files for the dataset to work with the `TransLogShiftingSimulation.py` simulation module.

- The `TransLogShiftingSimulation.py` has been updated and organized into classes instead of separate functions for all. This is for easy readability for next few users. 

#### [12/03/2020]
- Speed increase by 10%

- Updated plots and prints such that each simulation would eventually:
    - Export discharge and arrival timings
    - Export all image diagnostics
    - Export all text diagnostics
    
#### [Prior]
- Anything prior to 12th March was updates on perfecting the model to begin with. Instead of improvements.

## Tips and Tricks I've Learnt for Speed Optimisation:
1. Using numpy for vectorized functions are really quick
2. For pandas dataframe, using `df.iat[x, y]` for extracting a single value is much faster
3. Randomisation can be slow, the fastest one would be `np.random.rand()`, although the values are between 0 and 1
4. Rounding can be slow too. If you want a value of either 0 or 1, you can `int(np.random.rand() + 0.5)`, since `int()` cuts the float
5. List comprehensions are always much faster than using `filter` or `map`. Although `filter` and `map` are much faster than using loops
6. Look at all the loops in the program and write lines to stop the loop from running if it's pointless to continue. Basically, add `break` in loops whenever you can
7. Using `enumerate` to find the index is much faster
