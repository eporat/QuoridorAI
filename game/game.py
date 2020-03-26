import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from itertools import product
from easyAI import TwoPlayersGame


HORIZONTAL = 0
VERTICAL = 1

MOVEMENT = 0
WALL = 1


class Game(TwoPlayersGame):
    def __init__(self, size):
        self.size = size
        self.nplayer = 1
        # self.players = players
        self.graph = nx.grid_2d_graph(self.size, self.size)

        for a, b in self.graph.edges():
            self.graph.add_edge(b, a)

        self.players_loc = [np.array([self.size // 2, 0]),
                        np.array([self.size // 2, self.size - 1])]
        self.wall_counts = [10, 10]
        self.vertical_walls = set()
        self.horizontal_walls = set()
        self.index = 0
        self.terminal = False
        self.special_edges = []
        self.end_loc = [self.size - 1, 0]

    def possible_moves(self):
        if self.is_over():
            return []

        actions = []
        p = self.players_loc[self.index]
        for cell in self.available_cells():
            actions.append((MOVEMENT, cell[0] - p[0], cell[1] - p[1]))

        if self.wall_counts[self.index] > 0:      
            for (x,y) in product(range(self.size), range(self.size)):
                if self.is_valid_vertical(x,y):
                    actions.append((WALL, x, y, VERTICAL))

                if self.is_valid_horizontal(x,y):
                    actions.append((WALL, x, y, HORIZONTAL))

        return actions

    @staticmethod
    def edges(x, y, orientation):
        if orientation == HORIZONTAL:
            return [((x, y), (x, y + 1)), ((x + 1, y), (x + 1, y + 1))]
        elif orientation == VERTICAL:
            return [((x, y), (x + 1, y)), ((x, y + 1), (x + 1, y + 1))]

    def is_valid_horizontal(self, x, y):
        if (x, y) in self.vertical_walls:
            return
        edges = Game.edges(x, y, HORIZONTAL)
        if (x, y) in self.horizontal_walls or (x - 1, y) in self.horizontal_walls or (x + 1, y) in self.horizontal_walls:
            return

        if not all(self.graph.has_edge(*edge) for edge in edges):
            return

        self.graph.remove_edges_from(edges)
        connected = self.check_connected()
        self.graph.add_edges_from(edges)

        if not connected:
            return False

        return edges

    def is_valid_vertical(self, x, y):
        if (x, y) in self.horizontal_walls:
            return
        edges = Game.edges(x, y, VERTICAL)
        if (x, y) in self.vertical_walls or (x, y - 1) in self.vertical_walls or (x, y + 1) in self.vertical_walls:
            return
        if not all(self.graph.has_edge(*edge) for edge in edges):
            return

        self.graph.remove_edges_from(edges)
        connected = self.check_connected()
        self.graph.add_edges_from(edges)

        if not connected:
            return False

        return edges

    def place_horizontal(self, x, y):
        edges = self.is_valid_horizontal(x, y)
        if not edges:
            return
        self.graph.remove_edges_from(edges)
        self.horizontal_walls.add((x,y))
        return edges

    def place_vertical(self, x, y):
        edges = self.is_valid_vertical(x, y)
        if not edges:
            return
        self.graph.remove_edges_from(edges)
        self.vertical_walls.add((x,y))
        return edges

    def unmake_move(self, move):
        if move[0] == MOVEMENT:
            self.players_loc[1 - self.index][0] -= move[1]
            self.players_loc[1 - self.index][1] -= move[2]
            self.terminal = self.players_loc[1 - self.index][1] == self.end_loc[1 - self.index]

        elif move[0] == WALL:
            self.graph.add_edges_from(Game.edges(move[1], move[2], move[3]))
            
            if move[3] == HORIZONTAL:
                self.horizontal_walls.remove((move[1], move[2]))
            elif move[3] == VERTICAL:
                self.vertical_walls.remove((move[1], move[2]))
            
            self.wall_counts[1 - self.index] += 1

        self.graph.remove_edges_from(self.special_edges)
        self.next_turn()
        self.find_special_edges()
        self.graph.add_edges_from(self.special_edges)

    def place_wall(self, x, y, orientation):
        if not self.wall_counts[self.index]:
            return False
        if x == self.size - 1 or y == self.size - 1:
            return False
        if orientation == HORIZONTAL:
            edges = self.place_horizontal(x, y)
        elif orientation == VERTICAL:
            edges = self.place_vertical(x, y)
        if not edges:
            return False
        self.wall_counts[self.index] -= 1
        return True

    def check_connected(self):
        # Make sure there are still ways to reach the end
        self.graph.remove_edges_from(self.special_edges)
        con1 = nx.node_connected_component(self.graph, tuple(self.players_loc[0]))
        con2 = nx.node_connected_component(self.graph, tuple(self.players_loc[1]))
        connected = any(y == self.size - 1 for x, y in con1) and any(y == 0 for x, y in con2)
        self.graph.add_edges_from(self.special_edges)
        return connected

    def move_player(self, direction_x, direction_y):
        direction = np.array([direction_x, direction_y])
        p = self.players_loc[self.index]
        if not self.has_edge(p, p + direction):
            return False
        self.players_loc[self.index] += direction
        if p[1] == (1 - self.size) * (self.index - 1):
            self.terminal = True
        return True

    def direction(self, i, j):
        return i - self.players_loc[self.index][0], j - self.players_loc[self.index][1]

    def next_turn(self):
        self.index = 1 - self.index

    def play_game(self, type, param1, param2=None, param3=None):
        if self.is_over():
            return
        if type == MOVEMENT:
            valid = self.move_player(direction_x=param1, direction_y=param2)
        elif type == WALL:
            valid = self.place_wall(x=param1, y=param2, orientation=param3)
        if not valid:
            return False
        self.graph.remove_edges_from(self.special_edges)
        self.next_turn()
        self.find_special_edges()
        self.graph.add_edges_from(self.special_edges)
        return True

    def available_cells(self):
        p = self.players_loc[self.index]
        o = self.players_loc[1 - self.index]
        return filter(lambda node: self.has_edge(p, node) and node != tuple(o) and node != (0, -1) and node != (0, self.size), self.graph.nodes())

    def find_special_edges(self):
        self.special_edges = []
        p1 = self.players_loc[self.index]
        p2 = self.players_loc[1 - self.index]
        vec = p2 - p1
        # 1 : jump forward 2 tiles: exists a tile and no WALL
        # 2 : jump diagonally: exists a tile infront of the direction...
        if np.abs(vec).sum() != 1:
            return
        if not self.has_edge(p1, p2):
            return
        if self.has_edge(p2, p2 + vec):
            self.special_edges.append((tuple(p1), tuple(p2 + vec)))
            return
        perp1 = np.roll(vec, 1)
        perp2 = - perp1
        for perp in (perp1, perp2):
            if self.has_edge(p2, p2 + perp):
                self.special_edges.append((tuple(p1), tuple(p2 + perp)))

    def has_edge(self, a, b):
        return self.graph.has_edge(tuple(a), tuple(b))

    def has_node(self, node):
        return self.graph.has_node(tuple(node))

    def make_move(self, action):
        self.play_game(*action)

    def is_over(self):
        return self.terminal

    def scoring(self):
        if self.players_loc[0][1] == self.size - 1:
            if self.index == 0:
                return 1000
            else:
                return -1000
        
        if self.players_loc[1][1] == 0:
            if self.index == 0:
                return -1000
            else:
                return 1000

        con1 = nx.node_connected_component(self.graph, tuple(self.players_loc[0]))
        con1 = filter(lambda x: x[1] == self.size - 1, con1)
        d1 = min(nx.shortest_path_length(self.graph, tuple(self.players_loc[0]), node) for node in con1)
        con2 = nx.node_connected_component(self.graph, tuple(self.players_loc[1]))
        con2 = filter(lambda x: x[1] == 0, con2)
        d2 = min(nx.shortest_path_length(self.graph, tuple(self.players_loc[1]), node) for node in con2)
        # d2 = nx.shortest_path_length(self.graph, tuple(self.players_loc[1]), (0, -1))        
        if self.index == 0:
            return d2 - d1
        else:
            return d1 - d2

    def __eq__(self, other):
        x = self.wall_counts == other.wall_counts
        y = all(np.array_equal(p, o) for (p,o) in zip(self.players_loc, other.players_loc))
        z = self.index == other.index
        return x and y and z
