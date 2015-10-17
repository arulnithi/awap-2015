import networkx as nx
import random
from base_player import BasePlayer
from settings import *

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
        self.weights = self.get_graph().copy()
        return

    # Checks if we can use a given path
    def path_is_valid(self, state, path):
        graph = state.get_graph()
        for i in range(0, len(path) - 1):
            if graph.edge[path[i]][path[i + 1]]['in_use']:
                return False
        return True

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

        # We have implemented a naive bot for you that builds a single station
        # and tries to find the shortest path from it to first pending order.
        # We recommend making it a bit smarter ;-)

        commands = []
        graph = state.get_graph()

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



        pending_orders = state.get_pending_orders()
        if len(pending_orders) != 0:
            order = random.choice(pending_orders)
            path = nx.shortest_path(graph, self.stations[0], order.get_node())
            if self.path_is_valid(state, path):
                commands.append(self.send_command(order, path))

        return commands
