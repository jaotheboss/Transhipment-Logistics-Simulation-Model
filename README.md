# Transhipment-Simulation-Model
Simulation Model of of the movement of containers from 1 location to another to ascertain its timeliness.

This project was inspired during my internship with PSA, with the objective of this simulation being:
    
    1. To determine the effects of the number of movers with regards to the containers arrival time
    
    2. Understand the activity pattern of each mover
    
    3. Observe the long term impacts of such a system
    
Note:

- Everything here was coded with Python and solely by myself. 

- The dataset used by this simulation cannot be provided.

- There were 2 original files, the model and execution file. However, i've come to realise the how messy things could get and have converted my 2 original files into 3 different kinds of files - Cleaning, Model and Execution

- All 3 of these files, except for the Execution file, are in class form for easier readability. 

#### Tips and Tricks I've Learnt for Speed Optimisation:
1. Using numpy for vectorized functions are really quick
2. For pandas dataframe, using `df.iat[x, y]` for extracting a single value is much faster
3. Randomisation can be slow, the fastest one would be `np.random.rand()`, although the values are between 0 and 1
4. Rounding can be slow too. If you want a value of either 0 or 1, you can `int(np.random.rand() + 0.5)`, since `int()` cuts the float
5. List comprehensions are always much faster than using `filter` or `map`. Although `filter` and `map` are much faster than using loops
6. Look at all the loops in the program and write lines to stop the loop from running if it's pointless to continue. Basically, add `break` in loops whenever you can
7. Using `enumerate` to find the index is much faster
