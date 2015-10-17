import networkx as nx
import random
from base_player import BasePlayer
from settings import *
import math

class Player(BasePlayer):
    """
    You will implement this class for the competition. DO NOT change the class
    name or the base class.
    """


    def __init__(self, state):
        """
        Initializes your Player. You can set up persistent state, do analysis
        on the input graph, engage in whatever pre-computation you need. This
        function must take less than Settings.INIT_TIMEOUT seconds.
        --- Parameters ---
        state : State
            The initial state of the game. See state.py for more information.
        """
        self.hubInRegion = HUBS/(GRAPH_SIZE/((SCORE_MEAN/DECAY_FACTOR)**2))
        self.stations = []
        self.weights = state.get_graph().copy()
        for i in xrange(GRAPH_SIZE):
            self.weights.node[i]["weight"] = 0
        return

    # Checks if we can use a given path
    def path_is_valid(self, state, path):
        graph = state.get_graph()
        for i in range(0, len(path) - 1):
            if graph.edge[path[i]][path[i + 1]]['in_use']:
                return False
        return True

    def normal(self, distance):
        return 1/((ORDER_VAR*2*math.pi)**0.5)*math.exp(-(distance**2/(2*ORDER_VAR)))


    def step(self, state):
        """
        Determine actions based on the current state of the city. Called every
        time step. This function must take less than Settings.STEP_TIMEOUT
        seconds.
        --- Parameters ---
        state : State
            The state of the game. See state.py for more information.
        --- Returns ---
        commands : dict list
            Each command should be generated via self.send_command or
            self.build_command. The commands are evaluated in order.
        """

        commands = []
        graph = state.get_graph()

        # Build command(s) for first move
        if (state.get_time() == 0 and self.hubInRegion >= 1):
            nodemap = nx.closeness_centrality(graph)
            center = 0
            closeness = 0
            for node in nodemap:
                if nodemap[node] > closeness:
                    center = node
                    closeness = nodemap[node]
            station = graph.nodes()[center]
            self.stations += [station]
            commands.append(self.build_command(center))

        # Update our copy of the graph
        self.update_graph(state)
        
        # Build additional stations
        if (self.profit(state) > 0 and state.get_money() > self.cost() and
            len(self.stations) < HUBS + 1):
            new_station = self.find_hub(state)
            if new_station != None:
                print "stations", self.stations
                print "new_station", new_station
                self.stations += [new_station]
                commands.append(self.build_command(new_station))
            # update graph values with placement of new station

        # Fulfill orders
        pending_orders = state.get_pending_orders()
        if len(pending_orders) != 0:
            order = random.choice(pending_orders)
            station = self.find_nearest_station()
            path = nx.shortest_path(graph, station, order.get_node())
            if self.path_is_valid(state, path):
                commands.append(self.send_command(order, path))

        return commands
    
    def update_graph(self, state):
        pending_orders = state.get_pending_orders()
        newOrder = None
        for order in pending_orders:
            if order.get_time_created() == state.get_time():
                newOrder = order
                break
        if newOrder != None:
            successors = nx.bfs_successors(self.weights, newOrder.node)
            nodes = [newOrder.node]
            for distance in xrange(int(2*ORDER_VAR)):
                nextNodes = []
                for node in nodes:
                    self.weights.node[node]["weight"] += self.normal(distance)
                    if node in successors:
                        nextNodes.extend(successors[node])
                nodes = nextNodes
        if state.get_time() == 999:
            for i in xrange(GRAPH_SIZE):
                print i, self.weights.node[i]["weight"]
    
    def profit(self, state):
        num_orders_fulfilled = ((GAME_LENGTH - state.get_time())*ORDER_CHANCE) / HUBS
        profit_per_order = SCORE_MEAN - (DECAY_FACTOR * ORDER_VAR)
        return (num_orders_fulfilled * profit_per_order) - self.cost()
    
    def cost(self):
        return INIT_BUILD_COST * (BUILD_FACTOR ** len(self.stations))
    
    
    def find_hub(self, state):
        listNodes = nx.nodes(self.weights)
        def nodeWeightCmp(node1, node2):
            return int(self.weights.node[node2]["weight"] - \
            self.weights.node[node1]["weight"])
        listNodes.sort(nodeWeightCmp)
        for posHub in listNodes:
            min_dist = self.min_distance_to_station(posHub, state)
            if (min_dist == None or min_dist > ORDER_VAR**0.5):
                return posHub
        return None

    def min_distance_to_station(self, node, state):
        dist = None
        for station in self.stations:
            distTemp = len(nx.shortest_path(state.get_graph(), node,station)) - 1
            if (dist == None or distTemp<dist):
                dist = distTemp
        return dist

    def find_nearest_station(self):
        return
