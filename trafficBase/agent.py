from mesa import Agent
import networkx as nx
import random

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
            self.calculate_ShortestPath()

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

        if self_tf:
            if self_tf.state: 
                if next_car == None:
                    return True
                else:
                    return False
            else:
                return False
            
        elif next_car:
            # Esto siguiente me puede causar problemas ya que se pueden combinar coches en los cruces
            if next_car.estado:
                return True
            else:
                #Aqui va toda la mecanica de recalcular el a*
                # self.can_changeLane()
                return False
        
        return True

    def calculate_ShortestPath(self):
        """ 
        Will calculate the shortest path to the destination, taking into account 3 steps ahead
        """
        self.path = nx.astar_path(self.model.graph, self.pos, self.destinationAgent.pos, weight='weight')[1:]
        # print(self.path)

    def can_changeLane(self):
        """ 
        Will calculate the shortest path if it can change lane
        """
        successors = self.model.graph.successors(self.pos)
        for i in successors:
            print(i)

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        self.move(self.model)
        # self.calculate_ShortestPath(self.model)
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