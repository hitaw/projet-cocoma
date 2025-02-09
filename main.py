from projet import environnement, taxi, task, GUI
import random

env = environnement(
    taille = 50, 
    num_taxis = 3, 
    freq_tasks = 120, 
    n_tasks = 4, 
    method = 1, #0 : random, 1 : DCOP, 2 : PSI, 3 : SSI, 4 : Regret, 5 : CBBA
    ordonnancement = 2, #0 : None, #1 : Held-Karp, 2 : Glouton
    heuristic = 0, #0 : Prim, 1 : Insert
    stop_number = 100,
    stop_condition = 1, #0 : None, 1 : Number of tasks, 2 : Number of iterations
    n_run = 10
    )
gui = GUI(env)
gui.run()