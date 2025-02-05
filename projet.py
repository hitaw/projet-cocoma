import random
import math
import pygame
import pydcop

class taxi:
    def __init__(self, id:int, position:tuple):
        self.id = id
        self.position = position
        self.float_position = list(position)
        self.destination = position
        self.tasks = []
        self.going_to_departure_point = True
        self.color = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    def move(self, next_position:tuple):
        self.float_position = next_position
        self.position = (round(self.float_position[0]), round(self.float_position[1]))

    def estimate_Prim(self, tasks : object):
        best_bid = (None, float("inf"), -1)
        for task_available in tasks:
            if self.going_to_departure_point: #Si je ne suis pas en train de faire une tâche
                min_cost = abs(self.position[0] - task_available.departure[0]) + abs(self.position[1] - task_available.departure[1])
            else: #Si je suis en train de faire une tâche, la position actuelle du taxi ne compte pas dans le calcul du coût minimal
                min_cost = math.inf
            for task_in_taxi in self.tasks:
                cost = abs(task_in_taxi.destination[0] - task_available.departure[0]) + abs(task_in_taxi.destination[1] - task_available.departure[1])
                if cost < min_cost:
                    min_cost = cost
            if min_cost < best_bid[1]:
                best_bid = (task_available, min_cost, -1)
        return best_bid
    
    def estimate_Insert(self, tasks : object):
        best_bid = (None, float("inf"), -1)
        for task_available in tasks:
            min_cost = math.inf
            pos = -1
            for i in range(len(self.tasks) + 1):
                if i == 0 and not self.going_to_departure_point: # Si on est en train de faire une tâche, on ne peut pas insérer une autre tâche avant
                    continue
                cost = self.calculate_cost(self.tasks[:i] + [task_available] + self.tasks[i:])
                if cost < min_cost:
                    min_cost = cost
                    pos = i
            if min_cost < best_bid[1]:
                best_bid = (task_available, min_cost, pos)
        return best_bid

    def assign(self, task:object, pos : int = -1):
        if pos != -1:
            self.tasks.insert(pos, task)
        else:
            self.tasks.append(task)
        task.allocated = True
        task.taxi = self

    def unassign(self, task:object):
        self.tasks.remove(task)

    def rearrange_tasks(self, ordonnancement:int):
        pass

    def calculate_cost(self, tasks:list):
        total_cost = 0
        end_position = self.position
        for task in tasks:
            total_cost += abs(end_position[0] - task.departure[0]) + abs(end_position[1] - task.departure[1])
            total_cost += task.cost
            end_position = task.destination
        return total_cost        

    def __str__(self):
        return f"Taxi {self.id} is at {self.position} and is going to {self.destination}"
    
class task:
    def __init__(self, id:int, departure:tuple, destination:tuple):
        self.id = id
        self.departure = departure
        self.destination = destination
        self.cost = abs(departure[0] - destination[0]) + abs(departure[1] - destination[1])
        self.allocated = False
        self.is_running = False
        self.taxi = None

class auctioneer:
    def __init__(self, taxis:list, method : int, heuristic:int, ordonnancement:int = 0):
        self.taxis = taxis
        self.method = method
        self.heuristic = heuristic

    def auction(self, tasks):
        if self.method == 0: #Random
            self.random_assignation(tasks)

        elif self.method == 1: #DCOP
            self.generate_dcop(tasks)
            self.dcop_assignation(tasks)

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
                taxi.rearrange_tasks(0)

    def random_assignation(self, tasks):
        """
        Assigns tasks to taxis randomly
        """
        to_assign = tasks.copy()
        for task_to_assign in to_assign:
            winner = random.choice(self.taxis)
            winner.assign(task_to_assign)

    def generate_dcop(self, tasks):
        """
        Generates a DCOP file for the assignment of tasks to taxis
        """
        
        raise NotImplementedError
    
    def dcop_assignation(self, tasks):
        """
        Assigns tasks to taxis using a DCOP
        """
        raise NotImplementedError
    
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

class environnement:
    def __init__(self, taille:int, num_taxis : int, freq_tasks : int, n_tasks : int, method : int, ordonnancement : int, heuristic : int, interface : bool = True):
        self.taille = taille
        self.num_taxis = num_taxis
        self.taxis = []
        for i in range(self.num_taxis):
            self.taxis.append(taxi(i, (random.randint(0, self.taille), random.randint(0, self.taille))))
        self.freq_tasks = freq_tasks
        self.n_tasks = n_tasks
        self.auctioneer = auctioneer(self.taxis, method, heuristic)
        self.interface = interface
        self.tasks = []
        self.time = -5
        self.ids = 0

    def step(self):
        if self.time % self.freq_tasks == 0:
            new_tasks = self.generate_task(self.n_tasks)
            self.auctioneer.auction(new_tasks)
            
        for taxi in self.taxis:
            if taxi.position == taxi.destination:
                if len(taxi.tasks) > 0:
                    if taxi.going_to_departure_point:
                        taxi.destination = taxi.tasks[0].departure
                        taxi.going_to_departure_point = False
                    else:
                        taxi.tasks[0].is_running = True
                        taxi.destination = taxi.tasks[0].destination
                        if taxi.position == taxi.tasks[0].destination:
                            taxi.unassign(taxi.tasks[0])
                            taxi.going_to_departure_point = True
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
        step_size = 0.5  # Détermine la vitesse de déplacement
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
            self.clock.tick(60)
        pygame.quit()