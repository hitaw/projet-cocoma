from projet import environnement, taxi, task, GUI
import random

for i in range(5):
    if i == 1 or i == 5:
        continue
    for j in range(3):
        if j == 1:
            continue
        for k in range(2):
            env = environnement(
                taille = 50, 
                num_taxis = 3, 
                freq_tasks = 120, 
                n_tasks = 4, 
                method = i, #0 : random, 1 : DCOP, 2 : PSI, 3 : SSI, 4 : Regret, 5 : CBBA
                ordonnancement = j, #0 : None, #1 : Held-Karp, 2 : Glouton
                heuristic = k, #0 : Prim, 1 : Insert
                stop_number = 100,
                stop_condition = 1, #0 : None, 1 : Number of tasks, 2 : Number of iterations
                n_run = 10
                )
            print("Method : ", i, " Ordonnancement : ", j, " Heuristic : ", k)
            gui = GUI(env)
            gui.run()
            print(" ")
            print("Fin de la simulation")