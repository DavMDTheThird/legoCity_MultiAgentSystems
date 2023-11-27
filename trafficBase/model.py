from mesa import Model, DataCollector
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json
import networkx as nx

class CityModel(Model):
    """ 
        Creates a model based on a city map.

        Args:
            N: Number of agents in the simulation
    """
    def __init__(self, N):

        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        dataDictionary = json.load(open("city_files/mapDictionary.json"))

        self.traffic_lights = []

        # Load the map file. The map file is a text file where each character represents an agent.
        with open('city_files/2022_base.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)
            self.numCars = 0
            self.destinationsList = []
            self.arrivedCarsList = []

            self.grid = MultiGrid(self.width, self.height, torus = False) 
            self.schedule = RandomActivation(self)

            self.datacollector = DataCollector( 
                model_reporters = {
                        "Car collision": lambda m: 1 if m.checkCollision() else 0,
            })

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row): #col es el signo
                    if col in ["v", "^", ">", "<", "g","h","b","n"]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col in ["R","r","L","l","U","u","D","d"]:
                        agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col in ["R","L","U","D"] else True, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "T":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.destinationsList.append(agent)

                    elif col == "C":
                        agent = Car_Generator(f"cg_{r*self.width+c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)

        
        # print(self.grid.get_cell_list_contents((5,0)))

        self.graph = self.create_graph()
        # print(self.graph.edges())
        # path = nx.astar_path(self.graph, (0,0), (19,1), weight='weight')
        # print(path)

        self.num_agents = N
        self.running = True

    def step(self):
        '''Advance the model by one step.'''
        self.deleteCars()
        self.schedule.step()
        self.datacollector.collect(self)

    
    def get_nextPossibleSteps(self, agent):
        ''' 
        Returns a list of the possible steps from the current position.
        '''
        # obtener los posibles pasos
        possible_steps = self.grid.get_neighborhood(
            agent.pos,
            moore=True, # includes diagonals
        ) # include_center=True) #Este no se si lo requerimos

        # quitar los obstaculos
        possible_steps = [step for step in possible_steps 
                          if not isinstance(self.grid[step[0]][step[1]][0], Obstacle)]
        
        if agent.direction == "Right":
            # quitar las calles que estan atrás o alado del agente
            possible_steps = [step for step in possible_steps if step[0] > agent.pos[0] or self.grid[step[0]][step[1]][0].direction  == "destination"]

            # quitar las calles que *vienen* hacia el agente
            possible_steps = [step for step in possible_steps if not 
                                   (step[1] > agent.pos[1] and self.grid[step[0]][step[1]][0].direction in ["Down", "Destination"]) and not
                                   (step[1] < agent.pos[1] and self.grid[step[0]][step[1]][0].direction in ["Up", "Destination"])]
            # print(agent.pos, possible_steps)
            
        elif agent.direction == "Left":
            # quitar las calles que estan atrás o alado del agente
            possible_steps = [step for step in possible_steps if step[0] < agent.pos[0]] # Le quito los de atras

            # quitar las calles que *vienen* hacia el agente
            possible_steps = [step for step in possible_steps if not 
                                   (step[1] < agent.pos[1] and self.grid[step[0]][step[1]][0].direction in ["Up", "Destination"]) and not
                                   (step[1] > agent.pos[1] and self.grid[step[0]][step[1]][0].direction in ["Down", "Destination"])]
            # print(agent.pos, possible_steps)
            
        elif agent.direction == "Up":
            # quitar las calles que estan atrás o alado del agente
            possible_steps = [step for step in possible_steps if step[1] > agent.pos[1]]

            # quitar las calles que *vienen* hacia el agente
            possible_steps = [step for step in possible_steps if not 
                                   (step[0] < agent.pos[0] and self.grid[step[0]][step[1]][0].direction in ["Left", "Destination"]) and not
                                   (step[0] > agent.pos[0] and self.grid[step[0]][step[1]][0].direction in ["Right", "Destination"])]
            # print(agent.pos, possible_steps)
            
        elif agent.direction == "Down":
            # quitar las calles que estan atrás o alado del agente
            possible_steps = [step for step in possible_steps if step[1] < agent.pos[1]]

            # quitar las calles que *vienen* hacia el agente
            possible_steps = [step for step in possible_steps if not 
                                   (step[0] < agent.pos[0] and self.grid[step[0]][step[1]][0].direction in ["Left", "Destination"]) and not
                                   (step[0] > agent.pos[0] and self.grid[step[0]][step[1]][0].direction in ["Right", "Destination"])]
            # print(agent.pos, possible_steps)
        
        # Aqui van las raritas
        elif agent.direction == "Up-Left":
            # quitar las calles que estan atrás o alado del agente
            possible_steps = [step for step in possible_steps if (step[0] < agent.pos[0] or (step[1] > agent.pos[1]))]
            
            # quitar las calles que *vienen* hacia el agente
            # possible_steps = [step for step in possible_steps if not 
            #                        (step[1] < agent.pos[1] and self.grid[step[0]][step[1]][0].direction in ["Up", "Right"])]
            # print(agent.pos, possible_steps)
            
        elif agent.direction == "Up-Right":
            # quitar las calles que estan atrás o alado del agente
            possible_steps = [step for step in possible_steps if (step[0] > agent.pos[0] or (step[1] > agent.pos[1]))]

            # quitar las calles que *vienen* hacia el agente
            # possible_steps = [step for step in possible_steps if not 
            #            (step[1] > agent.pos[1] and self.grid[step[0]][step[1]][0].direction in ["Down", "Left"])]
            # print(agent.pos, possible_steps)
            
        elif agent.direction == "Down-Left":
            # quitar las calles que estan atrás o alado del agente
            possible_steps = [step for step in possible_steps if (step[0] < agent.pos[0] or (step[1] < agent.pos[1]))]
            # print(agent.pos, possible_steps)
            
        elif agent.direction == "Down-Right":
            # quitar las calles que estan atrás o alado del agente
            # possible_steps = [step for step in possible_steps if (step[0] > agent.pos[0] or (step[1] < agent.pos[1]))]
            possible_steps = [step for step in possible_steps if step[1] <= agent.pos[1]]
            possible_steps = [step for step in possible_steps if step[0] >= agent.pos[0]]
            # print(agent.pos, possible_steps)
        
        # if agent.pos == (0, 23):
        #     print(agent.pos, possible_steps)
        return possible_steps
            
    
    def create_graph(self):
        ''' Creates a graph of the roads of the city map. '''
        DG = nx.DiGraph()
        for i in range(self.width):
            for j in range(self.height):
                # print(self.grid[i][j])
                if isinstance(self.grid[i][j][0], Road) or isinstance(self.grid[i][j][0], Traffic_Light) or isinstance(self.grid[i][j][0], Car_Generator):
                    possibleSteps = self.get_nextPossibleSteps(self.grid[i][j][0])
                    # print(f"{i},{j}", possibleSteps)
                    if possibleSteps: # Solo si possibleSteps no esta vacia
                        for step in possibleSteps:
                            #Super cheap forma de hacer que no vayan y se crucen a otro semaforo (mejorar)
                            if isinstance(self.grid[step[0]][step[1]][0], Traffic_Light):
                                DG.add_edge((i,j), step, weight=2)
                            else:
                                DG.add_edge((i,j), step, weight=1)
        return DG
    
    def deleteCars(self):
        if self.arrivedCarsList:
            for i in self.arrivedCarsList:
                self.grid.remove_agent(i)
                self.schedule.remove(i)
            
            self.arrivedCarsList = []

        for destination in self.destinationsList:
            for agent in  self.grid[destination.pos[0]][destination.pos[1]]:
                if isinstance(agent, Car):
                    self.arrivedCarsList.append(agent)

    def checkCollision(self):
        for i in range(self.width):
            for j in range(self.height):
                if len(self.grid[i][j]) >= 3:
                    for x in self.grid[i][j]:
                        if isinstance(x, Destination):
                            return False
                    print("---------------------")
                    print(f"Colition at: ({i}, {j})")
                    for x in self.grid[i][j]:
                        if not isinstance(x, Road):
                            print(x.unique_id)
                    self.running = False
                    return True

        