from mesa import Agent
import networkx as nx
import random
import copy


class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model, destinationAgent):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        self.destinationAgent = destinationAgent
        self.path = []
        self.estado = True


        super().__init__(unique_id, model)

    def move(self, model):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        if self.path == []:
            self.calculate_ShortestPath(self.model.graph)

        if self.path:
            if self.canMove(model):
                self.estado = True
                next_move = self.path.pop(0)
                model.grid.move_agent(self, next_move)
            else:
                self.estado = False

    def canMove(self, model):
        """
        Determines if the agent can move in the direction that was chosen
        """
        next_move = self.path[0]

        next_car = None
        self_tf = None

        for agent in model.grid[self.pos[0]][self.pos[1]]:
            if isinstance(agent, Traffic_Light):
                self_tf = agent
        for agent in model.grid[next_move[0]][next_move[1]]:
            if isinstance(agent, Car):
                next_car = agent

        # En semaforo
        if self_tf:
            if self_tf.state: 
                if next_car == None:
                    return True
                else:
                    return False
            else:
                return False
            
        # Coche adelate
        elif next_car:
            if self.changeLane():
                return True

            return False
            # # Esto siguiente me puede causar problemas ya que se pueden combinar coches en los cruces
            # if next_car.estado:
            #     return True
            # else:
            #     #Aqui va toda la mecanica de recalcular el a*
            #     return False
        
        return True

    def calculate_ShortestPath(self, graph):
        """ 
        Will calculate the shortest path to the destination, taking into account 3 steps ahead
        """
        self.path = nx.astar_path(graph, self.pos, self.destinationAgent.pos, weight='weight')[1:]
        # print(self.path)


    # def can_changeLane(self):
    #     """
    #     Determines is my car has no car on his sides
    #     """


    def changeLane(self):
        """ 
        Will calculate the shortest path if it can change lane
        """
        if len(self.path) >= 5:
            # print("--------------",self.pos, "--------------", "changeLane")
            successors = list(self.model.graph.successors(self.pos))
            
            # print(successors)
            next_successors = []
            for i in successors:
                next_successors.append(list(self.model.graph.successors(i)))

            successors = list(zip(successors, next_successors))

            graph_copy = copy.deepcopy(self.model.graph)

            for f in successors:
                # print("f:", f)
                next_step = self.model.grid[f[0][0]][f[0][1]]
                for g in next_step:
                    if isinstance(g, Car):
                        # print("self.pos:", self.pos, "g.pos", g.pos)
                        graph_copy[self.pos][g.pos]['weight'] = 1000

                for h in f[1]:
                    next_next_step = self.model.grid[h[0]][h[1]]
                    for l in next_next_step:
                        if isinstance(l, Car):
                            # print("f:", f, "l.pos",l.pos)
                            graph_copy[f[0]][l.pos]['weight'] = 1000
                            
            self.path = nx.astar_path(graph_copy, self.pos, self.destinationAgent.pos, weight='weight')[1:]

            # Check if the path is valid
            if self.path:
                next_move_agents = self.model.grid[self.path[0][0]][self.path[0][1]]
                for z in next_move_agents:
                    if isinstance(z, Car):
                        return False
                
            return True

        else:
            return False

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        self.move(self.model)
#----------------------------------------------------------------------------------------------
class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state = False, list_TimeToChange_Direction = [10,"Left"]):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red (False = red, True = green)
            list_TimeToChange_Direction: After how many step should the traffic light change color and
                                         in what direction is the traffic light facing.
        """
        self.state = state
        self.timeToChange = list_TimeToChange_Direction[0]
        self.direction = list_TimeToChange_Direction[1]

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state
#----------------------------------------------------------------------------------------------
class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.direction = "destination"

    def step(self):
        pass
#----------------------------------------------------------------------------------------------
class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass
#----------------------------------------------------------------------------------------------
class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass
#----------------------------------------------------------------------------------------------
class Car_Generator(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, list_TimeToGenerate_Direction = [10,"CarGenerator"]):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the car generator is active to generate cars
            timeToChange: After how many step should the car generator create another car 
        """
        self.timeToGenerate = list_TimeToGenerate_Direction[0]
        self.direction = list_TimeToGenerate_Direction[1]

    def generate_Car(self, model):
        # print(len(model.grid[self.pos[0]][self.pos[1]]))
        if len(model.grid[self.pos[0]][self.pos[1]]) <= 1:
            destinationAgent = random.choice(model.destinationsList)
            agent = Car(f"c_{self.pos[0]} {self.pos[1]} {model.numCars +1000}", model, destinationAgent)
            model.numCars += 1
            model.grid.place_agent(agent, self.pos)
            model.schedule.add(agent)


    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToGenerate == 0:
            self.generate_Car(self.model)