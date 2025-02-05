from projet import environnement, taxi, task, GUI
import random

env = environnement(
    taille = 50, 
    num_taxis = 3, 
    freq_tasks = 120, 
    n_tasks = 4, 
    method = 4, #0 : random, 1 : DCOP, 2 : PSI, 3 : SSI, 4 : Regret, 5 : CBBA
    ordonnancement = 0, #0 : None, #1 : Greedy
    heuristic = 1 #0 : Prim, 1 : Insert
    )


gui = GUI(env)
gui.run()
