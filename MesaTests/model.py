from mesa import Model, DataCollector
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json
import networkx as nx
# import requests

class CityModel(Model):
    """ 
        Creates a model based on a city map.
    """
    def __init__(self):
        # Cargar el diccionario del mapa. El diccionario asigna los caracteres del archivo de mapa al agente correspondiente.
        dataDictionary = json.load(open("legoCity_Agents/city_files/mapDictionary.json"))

        self.traffic_lights = []

        # Cargue el archivo del mapa. El archivo de mapa es un archivo de texto donde cada personaje representa un agente.
        with open('legoCity_Agents/city_files/base_city_2023.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)
            self.numCars = 0
            self.destinationsList = []
            self.arrivedCarsList = []

            # Numero de carros que han llegado a su destino (para la competencia)
            self.numArrivedCars = 0

            self.grid = MultiGrid(self.width, self.height, torus = False) 
            self.schedule = RandomActivation(self)

            # Detección de coliciones 
            self.datacollector = DataCollector( 
                model_reporters = {
                        "Car collision": lambda m: 1 if m.checkCollision() else 0,
            })

            # Revisa cada personaje en el archivo de mapa y crea el agente correspondiente.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):

                    # Todos los posibles agentes que puede recibir el mapa (en la lectura del txt)
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

        # Crear el grafo para sacar las rutas mas cortas para cada agente
        self.graph = self.create_graph()
        # print(self.graph.edges())
        # path = nx.astar_path(self.graph, (0,0), (19,1), weight='weight')
        # print(path)

        self.running = True

    def step(self):
        '''Advance the model by one step.'''
        print(f"Step: {self.schedule.steps}")
        self.deleteCars()
        self.schedule.step()
        self.datacollector.collect(self)

        # if self.schedule.steps % 100 == 0:
        #     self.concurso()

        # Parar en el step 1000
        if self.schedule.steps == 1001:
            self.running = False

    
    def get_nextPossibleSteps(self, agent):
        ''' 
        Returns a list of the possible steps from the current position.
        '''
        # obtener los posibles pasos
        possible_steps = self.grid.get_neighborhood(
            agent.pos,
            moore=True, # includes diagonals
        )

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
            
        elif agent.direction == "Left":
            # quitar las calles que estan atrás o alado del agente
            possible_steps = [step for step in possible_steps if step[0] < agent.pos[0]] # Le quito los de atras

            # quitar las calles que *vienen* hacia el agente
            possible_steps = [step for step in possible_steps if not 
                                   (step[1] < agent.pos[1] and self.grid[step[0]][step[1]][0].direction in ["Up", "Destination"]) and not
                                   (step[1] > agent.pos[1] and self.grid[step[0]][step[1]][0].direction in ["Down", "Destination"])]
            
        elif agent.direction == "Up":
            # quitar las calles que estan atrás o alado del agente
            possible_steps = [step for step in possible_steps if step[1] > agent.pos[1]]

            # quitar las calles que *vienen* hacia el agente
            possible_steps = [step for step in possible_steps if not 
                                   (step[0] < agent.pos[0] and self.grid[step[0]][step[1]][0].direction in ["Left", "Destination"]) and not
                                   (step[0] > agent.pos[0] and self.grid[step[0]][step[1]][0].direction in ["Right", "Destination"])]
            
        elif agent.direction == "Down":
            # quitar las calles que estan atrás o alado del agente
            possible_steps = [step for step in possible_steps if step[1] < agent.pos[1]]

            # quitar las calles que *vienen* hacia el agente
            possible_steps = [step for step in possible_steps if not 
                                   (step[0] < agent.pos[0] and self.grid[step[0]][step[1]][0].direction in ["Left", "Destination"]) and not
                                   (step[0] > agent.pos[0] and self.grid[step[0]][step[1]][0].direction in ["Right", "Destination"])]
        
        # Aqui van las raritas
        elif agent.direction == "Up-Left":
            # quitar las calles que estan atrás o alado del agente
            possible_steps = [step for step in possible_steps if (step[0] < agent.pos[0] or (step[1] > agent.pos[1]))]
            
        elif agent.direction == "Up-Right":
            # quitar las calles que estan atrás o alado del agente
            possible_steps = [step for step in possible_steps if (step[0] > agent.pos[0] or (step[1] > agent.pos[1]))]
            
        elif agent.direction == "Down-Left":
            # quitar las calles que estan atrás o alado del agente
            possible_steps = [step for step in possible_steps if (step[0] < agent.pos[0] or (step[1] < agent.pos[1]))]
            
        elif agent.direction == "Down-Right":
            # quitar las calles que estan atrás o alado del agente
            # possible_steps = [step for step in possible_steps if (step[0] > agent.pos[0] or (step[1] < agent.pos[1]))]
            possible_steps = [step for step in possible_steps if step[1] <= agent.pos[1]]
            possible_steps = [step for step in possible_steps if step[0] >= agent.pos[0]]
        
        return possible_steps
            
    
    def create_graph(self):
        ''' Creates a graph of the roads of the city map. '''
        DG = nx.DiGraph()
        # Recorrer todo el grid
        for i in range(self.width):
            for j in range(self.height):
                # Si encuentra algo que no sea un obstaculo
                if isinstance(self.grid[i][j][0], (Road, Traffic_Light, Car_Generator)):
                    # Obtener sus posibles siguientes pasos (direccion de la calle)
                    possibleSteps = self.get_nextPossibleSteps(self.grid[i][j][0])
                    # Por si regresa algo vacio
                    if possibleSteps:
                        for step in possibleSteps:
                            # Super cheap forma de hacer que no vayan y se crucen a otro semaforo (posible mejora)
                            if isinstance(self.grid[step[0]][step[1]][0], Traffic_Light):
                                DG.add_edge((i,j), step, weight=2)
                            else:
                                DG.add_edge((i,j), step, weight=1)
        return DG
    
    def deleteCars(self):
        # Si la lista tiene mas de 0 elementos
        if self.arrivedCarsList:
            # Eliminar los carros de la lista
            for i in self.arrivedCarsList:
                # Incrementar el recuento de carros que llegaron a su destino
                self.numArrivedCars += 1

                # Quitar carros
                self.grid.remove_agent(i)
                self.schedule.remove(i)
            
            # Limpiar la lista
            self.arrivedCarsList = []

        # Agregar a la lista los carros que ya llegaron a su destino (para que el siguiente step los elimine)
        for destination in self.destinationsList:
            for agent in  self.grid[destination.pos[0]][destination.pos[1]]:
                # Si hay un coche en uno de mis posibles destinos
                if isinstance(agent, Car):
                    self.arrivedCarsList.append(agent)

    def checkCollision(self):
        # Recorre todo el grid para ver si existe el caso de que hayan 3 o mas agentes en una misma posicion (significando que alguien chocó)
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


    # def concurso(self):

    #         url = "http://52.1.3.19:8585/api/"
    #         endpoint = "attempts"

    #         data = {
    #             "year" : 2023,
    #             "classroom" : 301,
    #             "name" : "LegoCity",
    #             "num_cars": self.numArrivedCars
    #         }

    #         headers = {
    #             "Content-Type": "application/json"
    #         }

    #         response = requests.post(url+endpoint, data=json.dumps(data), headers=headers)

    #         print("Request " + "successful" if response.status_code == 200 else "failed", "Status code:", response.status_code)
    #         print("Response:", response.json())
        