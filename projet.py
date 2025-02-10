import random
import math
import pygame
import pydcop
import yaml
import subprocess
import itertools
import time
import os

class taxi:
    def __init__(self, id:int, position:tuple):
        self.id = id
        self.position = position
        self.float_position = list(position)
        self.destination = position
        self.tasks = []
        self.tasks_done = []
        self.is_on_task = False
        self.color = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    def move(self, next_position:tuple):
        """
        Déplacement du taxi vers la prochaine position
        """
        self.float_position = next_position
        self.position = (round(self.float_position[0]), round(self.float_position[1]))

    def assign(self, task:object, pos : int = -1):
        """
        Attribution d'une tâche au taxi à une position donnée
        """
        if pos != -1:
            self.tasks.insert(pos, task)
        else:
            self.tasks.append(task)
        task.allocated = True
        task.taxi = self

    def unassign(self, task:object):
        """
        Désallocation d'une tâche au taxi, ajout de la tâche à la liste des tâches effectuées
        """
        self.tasks_done.append(task)
        self.tasks.remove(task)
    
    def calculate_cost(self, tasks:list):
        """
        Calcul du coût total de l'ensemble des tâches à effectuer
        """
        total_cost = 0
        end_position = self.position
        for task in tasks:
            total_cost += abs(end_position[0] - task.departure[0]) + abs(end_position[1] - task.departure[1])
            total_cost += task.cost
            end_position = task.destination
        return total_cost 

    def build_dist_matrix(self):
        """
        Construction de la matrice de distances entre les tâches à effectuer
        """

        if self.is_on_task:
            taxi_start = self.destination
            tasks_to_arrange = self.tasks[1:]
            path = [self.tasks[0]]
        else:
            taxi_start = self.position
            tasks_to_arrange = self.tasks
            path = []

        n = len(tasks_to_arrange) + 1

        dist_matrix = [[0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    dist_matrix[i][j] = 0
                elif j == 0:
                    dist_matrix[i][j] = 0
                elif i == 0:
                    dist_matrix[i][j] = abs(taxi_start[0] - tasks_to_arrange[j - 1].departure[0]) + abs(taxi_start[1] - tasks_to_arrange[j - 1].departure[1])
                else:
                    dist_matrix[i][j] = abs(tasks_to_arrange[i - 1].destination[0] - tasks_to_arrange[j - 1].departure[0]) + abs(tasks_to_arrange[i - 1].destination[1] - tasks_to_arrange[j - 1].departure[1])
        
        return dist_matrix, tasks_to_arrange, taxi_start, path
        
    def rearrange_tasks(self, ordonnancement:int):
        """
        Réorganisation des tâches du taxi selon l'ordonnancement choisi
        """
        
        dist_matrix, tasks_to_arrange, current_position, path = self.build_dist_matrix()

        if ordonnancement == 0:
            return
        
        elif ordonnancement == 1:
            raise NotImplementedError
            if len(self.tasks) > 2:
                print(f"Taxi {self.id} is rearranging {len(self.tasks)} tasks")
                path = path + self.held_karp(dist_matrix, tasks_to_arrange)
                self.tasks = path

        elif ordonnancement == 2:
            self.tasks = path + self.glouton(tasks_to_arrange, current_position)

    def glouton(self, tasks:list, current_position:tuple):
        """
        Algorithme glouton pour résoudre le problème de l'ordonnancement des tâches
        """
        final_path = []
        while len(tasks) > 0:
            min_cost = math.inf
            best_task = None
            for task in tasks:
                cost = abs(current_position[0] - task.departure[0]) + abs(current_position[1] - task.departure[1])
                if cost < min_cost:
                    min_cost = cost
                    best_task = task
            final_path.append(best_task)
            current_position = best_task.destination
            tasks.remove(best_task)
        return final_path
    
    def held_karp(self, dist_matrix:list, tasks:list):
        """
        Algorithme de Held-Karp pour résoudre le problème de l'ordonnancement des tâches
        """

        n = len(dist_matrix)
        if n < 2:
            return tasks
        C = {}
    
        # Initialisation : Distance du point de départ à chaque autre point
        for k in range(1, n):
            C[(1 << k, k)] = (dist_matrix[0][k], 0) # (distance, predecesseur)

        print(f"SELF IS ON TASK : {self.is_on_task}")
        print(f"Matrice de coûts : {dist_matrix}")
        print(f"Init C : {C}")
        # Remplissage de C
        for subset_size in range(2, n):  # Taille des sous-ensembles
            print(f"Subset size : {subset_size}")
            for subset in itertools.combinations(range(1, n), subset_size):  
                print(f"Subset : {subset}")
                bits = 0
                for bits in subset:
                    print(f"Bits : {bits}")
                    bits |= 1 << k

                for k in subset:
                    prev_bits = bits & ~(1 << k)

                    res = []                    
                    for m in subset:
                        if m == k or m == 0:
                            continue
                        print(f"prev_bits : {prev_bits}, m : {m}, k : {k}")
                        print(f"C[(prev_bits, m)] : {C[(prev_bits, m)]}")
                        print(f"dist_matrix[m][k] : {dist_matrix[m][k]}")
                        res.append((C[(prev_bits, m)][0] + dist_matrix[m][k], m))

        # Récupération du chemin optimal
        bits = (2 ** n - 1) - 1  # Tous les points sauf 0
        print(f"Bits : {bits}")

        res = []
        for k in range(1, n):
            res.append((C[(bits, k)][0] + dist_matrix[k][0], k))
        opt, parent = min(res)

        # Reconstruction du chemin
        path = []
        print(f"Matrice de coûts : {dist_matrix}")
        print(f"C : {C}")
        for i in range(n - 1):
            path.append(parent)
            new_bits = bits & ~(1 << parent)
            _, parent = C[(bits, parent)]
            bits = new_bits
        
        path.append(0)
        return [tasks[i] for i in path]

    # Algorithmes d'estimation du coût marginal pour la partie 3 : Négociation       
    def estimate_Prim(self, tasks : object):
        """
        Estimation du coût marginal de l'ajout d'une tâche à la liste des tâches du taxi avec l'heuristique de Prim
        """
        best_bid = (None, float("inf"), -1)
        for task_available in tasks:
            if not self.is_on_task: #Si je ne suis pas en train de faire une tâche
                min_cost = abs(self.position[0] - task_available.departure[0]) + abs(self.position[1] - task_available.departure[1])
            else: #Si je suis en train de faire une tâche, la position actuelle du taxi ne compte pas dans le calcul du coût minimal
                min_cost = math.inf
            for task_in_taxi in self.tasks:
                cost = abs(task_in_taxi.destination[0] - task_available.departure[0]) + abs(task_in_taxi.destination[1] - task_available.departure[1])
                if cost < min_cost:
                    min_cost = cost
            if min_cost < best_bid[1]:
                best_bid = (task_available, min_cost, -1) #déjà coût marginal
        return best_bid
    
    def estimate_Insert(self, tasks : object):
        """
        Estimation du coût marginal de l'ajout d'une tâche à la liste des tâches du taxi avec l'heuristique d'insertion
        """
        best_bid = (None, float("inf"), -1)
        for task_available in tasks:
            min_cost = math.inf
            pos = -1
            for i in range(len(self.tasks) + 1):
                if i == 0 and self.is_on_task: # Si on est en train de faire une tâche, on ne peut pas insérer une autre tâche avant
                    continue
                cost = self.calculate_cost(self.tasks[:i] + [task_available] + self.tasks[i:])
                if cost < min_cost:
                    min_cost = cost
                    pos = i
            if min_cost < best_bid[1]:
                best_bid = (task_available, min_cost, pos)
        return (task_available, min_cost - self.calculate_cost(self.tasks), pos) #coût marginal
    
    def __str__(self):
        return f"Taxi {self.id} is at {self.position} and is going to {self.destination}"
    
class task:
    def __init__(self, id:int, departure:tuple, destination:tuple):
        self.id = id
        self.departure = departure
        self.destination = destination
        self.cost = abs(departure[0] - destination[0]) + abs(departure[1] - destination[1])
        self.allocated = False
        self.taxi = None

class auctioneer:
    def __init__(self, taxis:list, method : int, heuristic:int, ordonnancement:int = 0):
        self.taxis = taxis
        self.method = method
        self.heuristic = heuristic
        self.ordonnancement = ordonnancement

    def auction(self, tasks):
        if self.method == 0: #Random
            self.random_assignation(tasks)

        elif self.method == 1: #DCOP
            self.generate_dcop(tasks)
            sol = self.dcop_assignation()
            print(f"Solution du DCOP : {sol}")

        elif self.method == 2: #PSI
            self.parallel_single_item_auction(tasks)

        elif self.method == 3: #SSI
            self.sequential_single_item_auction(tasks)

        elif self.method == 4: #Regret
            self.regret_auction(tasks)

        elif self.method == 5: #CBBA
            self.cbba_auction(tasks)

        if self.heuristic == 0:
            for taxi in self.taxis:
                taxi.rearrange_tasks(self.ordonnancement)

    def random_assignation(self, tasks):
        """
        Assigns tasks to taxis randomly
        """
        to_assign = tasks.copy()
        for task_to_assign in to_assign:
            winner = random.choice(self.taxis)
            winner.assign(task_to_assign)

    def generate_dcop(self, tasks, output_file="dcop_tasks.yml"):
        """
        Génère un fichier YAML pour un problème d'allocation de tâches entre taxis en DCOP.
        
        :param tasks: Liste des tâches (ex: ["task_A", "task_B"])
        :param output_file: Nom du fichier de sortie
        """
        
        with open(output_file, "w") as f:
            #Nom
            f.write("name: dcop_tasks\n\n")

            #Objectif : minimisation
            f.write("objective: min\n\n")

            #Domaines : taches, les valeurs sont les positions des tâches
            f.write("domains:\n")
            f.write("  task_domain:\n")
            f.write("    values: [")
            ids = ["t" + str(task.id) for task in tasks]
            combinaisons = []
            for i in range(len(tasks) + 1):
                for comb in itertools.combinations(ids, i):
                    #on veut ecrire sous la forme t1, t1t2, t1t3
                    if comb == ():
                        combinaisons.append("Vide")
                    else:
                        combinaisons.append("".join(comb))
            f.write(", ".join(combinaisons))
            f.write("]\n")
            f.write("    type: non_semantic")

            #Variables : 1 variable associée à chaque taxi
            f.write("\nvariables:\n")
            variables = [f"taxi_{taxi.id}" for taxi in self.taxis]
            for var in variables:
                f.write(f"  {var}:\n")
                f.write("    domain: task_domain\n")

            #Contraintes 
            f.write("\nconstraints:\n")
            
            for var in variables:
                name_fun = f"  cost_task_{var}:\n"
                f.write(name_fun)
                f.write("    type: extensional\n")
                f.write(f"    variables: {var}\n")
                f.write("    values:\n")
                fn = ""
                taxi = self.taxis[int(var[-1])]
                actual_cost = taxi.calculate_cost(taxi.tasks)
                fn += f'      {actual_cost}: Vide\n'
                for comb in combinaisons:
                    for task in tasks:
                        if comb != "Vide" and (f"t{task.id}" in comb):
                            tasks_to_add = [task for task in tasks if f"t{task.id}" in comb]
                            position = taxi.position
                            taxi_tasks = taxi.tasks
                            if taxi.is_on_task:
                                position = taxi.tasks[0].destination
                                taxi_tasks = taxi.tasks[1:]
                            path = taxi.glouton(taxi_tasks + tasks_to_add, position)
                            cost = taxi.calculate_cost(path)
                            fn += f'      {cost}: {comb}\n'
                            break
                f.write(fn)

            f.write("  too_many_assigned:\n")
            f.write("    type: intention\n")
            f.write("    function: |\n")
            fn = "      100000 if "
            #Si une tâche est assignée + d'une fois : pénalité
            for i in range(len(variables)):
                var = variables[i]
                for var2 in variables[i+1:]:
                    for comb in combinaisons:
                        for comb2 in combinaisons:
                            if comb != comb2 and comb != "Vide" and comb2 != "Vide" and (comb in comb2 or comb2 in comb):
                                fn += f"({var} == '{comb}' and {var2} == '{comb2}') or "

            fn = fn[:-4]
            f.write(fn + " else 0\n")

            f.write("  not_every_task_assigned:\n")
            f.write("    type: intention\n")
            f.write("    function: |\n")
            fn = "      100000 if ("
            for id in ids:
                for comb in combinaisons:
                    if comb != "Vide" and (id in comb):
                        for var in variables:
                            fn += f"{var} != '{comb}' and "
                fn = fn[:-4]
                fn += ") or ("
            fn = fn[:-4]
            f.write(fn + " else 0\n")

            f.write("\nagents:\n")
            for taxi in self.taxis:
                f.write(f"    a{taxi.id}:\n")
                f.write(f"      capacity: 1000\n")
            
    
    def dcop_assignation(self, algorithm="dpop", file_path="dcop_tasks.yaml"):
        """
        Assigns tasks to taxis using a DCOP
        """
        try:
            # Vérifier si le fichier YAML est valide
            with open(file_path, "r") as f:
                dcop_data = yaml.safe_load(f)

            print(f"Fichier DCOP chargé : {file_path}")
            
            # Commande Pydcop pour résoudre le DCOP
            command = f"pydcop solve --algo {algorithm} dcop_tasks.yaml"

            with open("resultats.json", "w") as result_file:
                result = subprocess.run(command, shell=True, stdout=result_file, stderr=subprocess.PIPE, executable = "/bin/bash")
            # Afficher la sortie brute de Pydcop
            print("Sortie brute de Pydcop :")
            print(result.stdout)

            # Vérifier les erreurs éventuelles
            if result.returncode != 0:
                print(f"Erreur lors de l'exécution de Pydcop : {result.stderr}")
                return None

            # Analyser et retourner la solution
            solution = yaml.safe_load(result.stdout)
            return solution
        
        except Exception as e:
            print(f"Erreur : {e}")
            return None

    
    def parallel_single_item_auction(self, tasks):
        """
        Assigns tasks to taxis using a parallel single item auction
        """

        to_assign = tasks.copy()
        bests_bids = []
        for task_to_assign in to_assign:
            bids = []
            for taxis in self.taxis:
                if self.heuristic == 0:
                    bid = taxis.estimate_Prim([task_to_assign])
                else:
                    bid = taxis.estimate_Insert([task_to_assign])
                bids.append(bid)
            best_bid = min(bids, key=lambda x: x[1])
            bests_bids.append((best_bid, self.taxis[bids.index(best_bid)]))
        
        for best_bid, winner in bests_bids:
            winner.assign(best_bid[0], best_bid[2])
            to_assign.remove(best_bid[0])

    def sequential_single_item_auction(self, tasks):
        """
        Assigns tasks to taxis using a sequential single item auction
        """

        to_assign = tasks.copy()
        while len(to_assign) > 0:
            bids = []
            for taxis in self.taxis:
                if self.heuristic == 0:
                    bid = taxis.estimate_Prim(to_assign)
                else:
                    bid = taxis.estimate_Insert(to_assign)
                bids.append(bid)
            best_bid = min(bids, key=lambda x: x[1])
            winner = self.taxis[bids.index(best_bid)]
            winner.assign(best_bid[0], best_bid[2])
            to_assign.remove(best_bid[0])
    
    def regret_auction(self, tasks):
        """
        Assigns tasks to taxis using a sequential single item auction based on regret
        """
        to_assign = tasks.copy()
        while len(to_assign) > 0:
            max_regret = -1
            overall_best_bid = (None, float("inf"), -1)
            winner = None
            for task_to_assign in to_assign:
                bids = []
                for taxis in self.taxis:
                    if self.heuristic == 0:
                        bid = taxis.estimate_Prim([task_to_assign])
                    else:
                        bid = taxis.estimate_Insert([task_to_assign])
                    bids.append(bid)
                best_bid = min(bids, key=lambda x: x[1])
                potential_winner = self.taxis[bids.index(best_bid)]
                bids.remove(best_bid)
                second_best_bid = min(bids, key=lambda x: x[1])
                regret = second_best_bid[1] - best_bid[1]
                if regret > max_regret:
                    max_regret = regret
                    overall_best_bid = best_bid
                    winner = potential_winner
            winner.assign(overall_best_bid[0], overall_best_bid[2])
            to_assign.remove(overall_best_bid[0])

    def cbba_auction(self, tasks):
        """
        Assigns tasks to taxis using the Consensus-Based Bundle Algorithm
        """
        raise NotImplementedError
    
class data_saver:
    def __init__(self, taxis:list, method:int, heuristic:int, ordonnancement:int, n_run:int):
        self.taxis = taxis
        if method == 0:
            self.method = "Random"
        elif method == 1:
            self.method = "DCOP"
        elif method == 2:
            self.method = "PSI"
        elif method == 3:
            self.method = "SSI"
        elif method == 4:
            self.method = "Regret"
        elif method == 5:
            self.method = "CBBA"
        if heuristic == 0:
            self.heuristic = "Prim"
        elif heuristic == 1:
            self.heuristic = "Insert"
        if ordonnancement == 0:
            self.ordonnancement = "None"
        elif ordonnancement == 1:
            self.ordonnancement = "Held-Karp"
        elif ordonnancement == 2:
            self.ordonnancement = "Glouton"
        self.nb_run = 0
        self.data = [[] for _ in range(n_run)]
        self.time_data = [0 for _ in range(n_run)]

    def save_data(self, tmps:float):
        for taxi in self.taxis:
            self.data[self.nb_run].append((taxi.id, len(taxi.tasks_done), taxi.calculate_cost(taxi.tasks_done)))
        self.time_data[self.nb_run] = tmps
        self.nb_run += 1
        
    def write_data(self, output_file):
        with open(output_file, "w") as f:
            title = f"Method : {self.method}, Heuristic : {self.heuristic}, Ordonnancement : {self.ordonnancement}\n"
            f.write("Taxi ID, Number of tasks completed, Total cost\n")
            for run in self.data:
                f.write(f"Run {self.data.index(run) + 1}\n")
                for line in run:
                    f.write(f"{line[0]},{line[1]},{line[2]}\n")

class environnement:
    def __init__(self, taille:int, num_taxis : int, freq_tasks : int, n_tasks : int, method : int, ordonnancement : int, heuristic : int, stop_number : int, stop_condition : int = 0, n_run : int = 1, interface : bool = True):
        self.taille = taille
        self.num_taxis = num_taxis
        self.taxis = []
        for i in range(self.num_taxis):
            self.taxis.append(taxi(i, (random.randint(0, self.taille), random.randint(0, self.taille))))
        self.freq_tasks = freq_tasks
        self.n_tasks = n_tasks
        self.auctioneer = auctioneer(self.taxis, method, heuristic, ordonnancement)
        self.data_saver = data_saver(self.taxis, method, heuristic, ordonnancement, n_run)
        self.interface = interface
        self.tasks = []
        self.time = -5
        self.ids = 0
        self.stop_number = stop_number
        self.stop_condition = stop_condition
        self.stop_simulation = False
        self.nb_run = 1
        self.n_run = n_run
        self.temps = 0

    def step(self):
        generating_tasks = True
        if self.stop_condition == 1 and self.ids >= self.stop_number:
            generating_tasks = False
        if self.stop_condition == 2 and self.time >= self.stop_number:
            generating_tasks = False

        if self.time == 0:
            self.temps = time.time()

        if self.time % self.freq_tasks == 0 and generating_tasks:
            new_tasks = self.generate_task(self.n_tasks)
            self.auctioneer.auction(new_tasks)

        if not generating_tasks and self.tasks == []:
            temps_run = time.time() - self.temps
            self.data_saver.save_data(temps_run)
            if self.nb_run < self.n_run:
                self.nb_run += 1
                self.time = -5
                self.ids = 0
                self.tasks = []
                generating_tasks = True
                for taxi in self.taxis:
                    taxi.position = (random.randint(0, self.taille), random.randint(0, self.taille))
                    taxi.float_position = list(taxi.position)
                    taxi.destination = taxi.position
                    taxi.tasks = []
                    taxi.tasks_done = []
                    taxi.is_on_task = False
            else:
                data_folder = "datas"
                if not os.path.exists(data_folder):
                    os.makedirs(data_folder)

                existing_files = os.listdir(data_folder)
                if existing_files:
                    existing_files.sort()
                    last_file = existing_files[-1]
                    last_file_number = int(last_file.split('_')[-1].split('.')[0])
                else:
                    last_file_number = 0

                new_file_number = last_file_number + 1
                new_file_name = f"data_run_{new_file_number}.txt"
                new_file_path = os.path.join(data_folder, new_file_name)
                self.data_saver.write_data(new_file_path)
                self.stop_simulation = True
            
        for taxi in self.taxis:
            if taxi.position == taxi.destination:
                if len(taxi.tasks) > 0:
                        if taxi.position == taxi.tasks[0].departure:
                            taxi.is_on_task = True

                        if not taxi.is_on_task:
                            taxi.destination = taxi.tasks[0].departure

                        else:
                            taxi.destination = taxi.tasks[0].destination
                            if taxi.position == taxi.tasks[0].destination:
                                taxi.unassign(taxi.tasks[0])
                                taxi.is_on_task = False
                else:
                    taxi.destination = taxi.position
            else:
                taxi.move(self.next_position(taxi.float_position, taxi.destination))
        self.clean_up_tasks()
        self.time += 1

    def generate_task(self, num_tasks:int):
        new_tasks = []
        for _ in range(num_tasks):
            departure = (random.randint(0, self.taille), random.randint(0, self.taille))
            destination = (random.randint(0, self.taille), random.randint(0, self.taille))
            new_task = task(self.ids, departure, destination)
            self.ids += 1
            new_tasks.append(new_task)
            self.tasks.append(new_task)
        return new_tasks

    def distance(self, pos1:tuple, pos2:tuple):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def next_position(self, position:tuple, destination:tuple):
        fx, fy = position
        dx, dy = destination
        step_size = 1  # Détermine la vitesse de déplacement
        vector_x = dx - fx
        vector_y = dy - fy
        distance = (vector_x**2 + vector_y**2)**0.5
        if distance == 0:
            return [fx, fy]
        return [fx + (vector_x / distance) * step_size, fy + (vector_y / distance) * step_size]
    
    def clean_up_tasks(self):
        self.tasks = [task for task in self.tasks if not task.allocated or any(task in taxi.tasks for taxi in self.taxis)]

class GUI:
    def __init__(self, environnement:object):
        self.env = environnement
        pygame.init()
        self.screen = pygame.display.set_mode((500, 500))
        pygame.display.set_caption("Taxi Simulation")
        self.clock = pygame.time.Clock()
        self.nb_run = 0

    def update_display(self):
        self.screen.fill((255, 255, 255))
        
        for taxi in self.env.taxis:

            x, y = taxi.float_position
            taxi_image = pygame.image.load("images/voiture_blanche.png")
            taxi_image = pygame.transform.scale(taxi_image, (40, 40))
            dx = taxi.destination[0] - taxi.position[0]
            dy = taxi.destination[1] - taxi.position[1]
            angle = math.degrees(math.atan2(-dy, dx)) + 90
            taxi_image = pygame.transform.rotate(taxi_image, angle)
            
            # Apply color filter to the taxi image
            colored_image = pygame.Surface(taxi_image.get_size()).convert_alpha()
            colored_image.fill(taxi.color)
            taxi_image.blit(colored_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            rect = taxi_image.get_rect(center=(x * 10 + 5, y * 10 + 5))
            self.screen.blit(taxi_image, rect.topleft)
            font = pygame.font.Font(None, 24)
            text = font.render(str(taxi.id), True, (255, 255, 255))
            self.screen.blit(text, (x * 10, y * 10))

        for task in self.env.tasks:

            x1, y1 = task.departure
            x2, y2 = task.destination
            if task.allocated:
                color = task.taxi.color
            else:
                color = (255, 0, 0)
            pygame.draw.ellipse(self.screen, color, (x1 * 10 - 5, y1 * 10 - 5, 20, 20))
            font = pygame.font.Font(None, 20)
            text = font.render(str(task.id), True, (255, 255, 255))
            text_rect = text.get_rect(center=(x1 * 10 + 5, y1 * 10 + 5))
            self.screen.blit(text, text_rect.topleft)
            pygame.draw.line(self.screen, color, (x1 * 10 + 5, y1 * 10 + 5), (x2 * 10 + 5, y2 * 10 + 5))
        pygame.display.flip()
        self.env.step()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.update_display()
            if self.env.stop_simulation:
                running = False
            self.clock.tick(60)
        pygame.quit()