import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

HORIZONTAL = 0
VERTICAL = 1

MOVEMENT = 0
WALL = 1

class Game:
    def __init__(self, size):
        self.size = size
        self.graph = nx.grid_2d_graph(self.size, self.size)

        for a, b in self.graph.edges():
            self.graph.add_edge(b, a)

        self.players = [np.array([self.size // 2,0]), np.array([self.size // 2, self.size - 1])]
        self.index = 0
        self.terminal = False
        self.special_edges = []

    def place_wall(self, x, y, orientation):
        if x == self.size - 1 or y == self.size - 1:
            return False

        if orientation == HORIZONTAL:
            edges = [((x, y), (x, y + 1)), ((x + 1, y), (x + 1, y + 1))]
            if not all(self.graph.has_edge(*edge) for edge in edges):
                return False
            if not self.graph.has_edge((x,y), (x, y + 1)):
                return False
            self.graph.remove_edges_from(edges)

        elif orientation == VERTICAL:
            edges = [((x, y), (x + 1, y)), ((x, y + 1), (x + 1, y + 1))]
            if not all(self.graph.has_edge(*edge) for edge in edges):
                return False

            if not self.graph.has_edge((x + 1,y), (x,y)):
                return False

            self.graph.remove_edges_from(edges)

        # Make sure there are still ways to reach the end
        self.graph.remove_edges_from(self.special_edges)

        con1 = nx.node_connected_component(self.graph, tuple(self.players[0]))
        con2 = nx.node_connected_component(self.graph, tuple(self.players[1]))

        self.graph.add_edges_from(self.special_edges)

        if not any(node[1] == self.size - 1 for node in con1) or not any(node[1] == 0 for node in con2):
            self.graph.add_edges_from(edges)
            return False

        return True

    def move_player(self, direction):
        p = self.players[self.index]

        if not self.has_edge(p, p + direction):
            return False

        self.players[self.index] += direction

        if self.players[self.index][1] == (1 - self.size) * (self.index - 1):
            self.terminal = True
            print("GAME OVER")

        return True

    def direction(self, i, j):
        return np.array([i,j]) - self.players[self.index]

    def next_turn(self):
        self.index = 1 - self.index

    def play(self, type, param1, param2=None, param3=None):
        if self.terminal:
            return

        if type == MOVEMENT:
            valid = self.move_player(direction=param1)

        if type == WALL:
            valid = self.place_wall(x=param1, y=param2, orientation=param3)

        if not valid:
            return False

        self.graph.remove_edges_from(self.special_edges)
        self.next_turn()
        self.find_special_edges()
        self.graph.add_edges_from(self.special_edges)

        return True

    def available_cells(self):
        p = self.players[self.index]
        o = self.players[1 - self.index]
        return filter(lambda node: self.has_edge(p, node) and node != tuple(o), self.graph.nodes())

    def find_special_edges(self):
        self.special_edges = []

        p1 = self.players[self.index]
        p2 = self.players[1 - self.index]
        vec = p2 - p1
        #1 : jump forward 2 tiles: exists a tile and no WALL
        #2 : jump diagonally: exists a tile infront of the direction...
        if np.abs(vec).sum() != 1:
            return

        if not self.has_edge(p1,p2):
            return
        # no wall
        if not self.has_node(p2 + vec):
            return

        if self.has_edge(p2, p2 + vec):
            self.special_edges.append((tuple(p1), tuple(p2 + vec)))
            return

        perp1 = np.roll(vec, 1)
        perp2 = -perp1

        for perp in (perp1, perp2):
             if self.has_edge(p2, p2 + perp):
                self.special_edges.append((tuple(p1), tuple(p2 + perp)))

    def has_edge(self, a, b):
        return self.graph.has_edge(tuple(a), tuple(b))

    def has_node(self, node):
        return self.graph.has_node(tuple(node))
