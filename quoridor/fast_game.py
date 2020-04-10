import sys
sys.path.insert(0,'..')
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from itertools import product
import copy
import random
from easyAI import TwoPlayersGame


HORIZONTAL = 0
VERTICAL = 1

MOVEMENT = 0
WALL = 1

WALL_SCORE = 0 # Notice that wall score is 0 now!!!
DISTANCE_SCORE = 1

DELTA = [(-2, 0), (2, 0), (0, 2), (0, -2), (-1, 1), (-1, -1), (1, -1), (1, 1), (0, 1), (0, -1), (1, 0), (-1, 0)]

MOVES = {}

class Game(TwoPlayersGame):
    def __init__(self, size):
        self.size = size
        self.wall_counts = [self.size + 1, self.size + 1]
        self.nplayer = 1
        # self.players = players
        self.graph = nx.grid_2d_graph(self.size, self.size)
        self.players_loc = [np.array([self.size // 2, 0]),
                        np.array([self.size // 2, self.size - 1])]

        self.vertical_walls = set()
        self.horizontal_walls = set()
        self.index = 0
        self.terminal = False
        self.special_edges = []
        self.end_loc = [self.size - 1, 0]
        self.availables = self.possible_moves()


    def distance(self, index, loc):
        return abs(self.players_loc[index][0] - loc[0]) + abs(self.players_loc[index][1] - loc[1])


    def possible_moves(self):
        if self.is_terminal():
            return []

        if hash(self) in MOVES:
            return MOVES[hash(self)]

        actions = []
        p = self.players_loc[self.index]
        o = self.players_loc[1 - self.index]

        for cell in sorted(self.available_cells(), key=lambda cell: abs(cell[0] - p[0]) + abs(cell[1] - p[1]), reverse=True):
             actions.append((MOVEMENT, cell[0] - p[0], cell[1] - p[1]))
        #for cell in self.available_cells():
        #    actions.append((MOVEMENT, cell[0] - p[0], cell[1] - p[1]))


        if self.wall_counts[self.index] > 0:
            # locations = sorted(self.graph.nodes(), key=lambda cell: abs(cell[0] - o[0]) + abs(cell[1] - o[1]))

            for x in range(self.size - 1):
                for y in range(self.size - 1):
                    if self.is_valid_vertical(x,y):
                        actions.append((WALL, x, y, VERTICAL))

                    if self.is_valid_horizontal(x,y):
                        actions.append((WALL, x, y, HORIZONTAL))

        #random.shuffle(actions) # exists already in negamax player!
        # The actions are sorted in a way that moves are first and walls are seconds
        # the moves are ordered by jumping moves and then normal moves
        MOVES[hash(self)] = actions

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

    def place_horizontal(self, x, y, check):
        if check:
            edges = self.is_valid_vertical(x, y)
        else:
            edges = Game.edges(x, y, HORIZONTAL)
        if not edges:
            return
        self.graph.remove_edges_from(edges)
        self.horizontal_walls.add((x,y))
        return edges

    def place_vertical(self, x, y, check):
        if check:
            edges = self.is_valid_vertical(x, y)
        else:
            edges = Game.edges(x,y,VERTICAL)
        if not edges:
            return
        self.graph.remove_edges_from(edges)
        self.vertical_walls.add((x,y))
        return edges
    '''
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
        self.availables = self.possible_moves()
    '''
    def place_wall(self, x, y, orientation, check=True):
        if not self.wall_counts[self.index]:
            return False
        if x == self.size - 1 or y == self.size - 1:
            return False
        if orientation == HORIZONTAL:
            edges = self.place_horizontal(x, y, check)
        elif orientation == VERTICAL:
            edges = self.place_vertical(x, y, check)
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

    def play_game(self, type, param1, param2=None, param3=None, check=False):
        if self.is_terminal():
            return
        if type == MOVEMENT:
            valid = self.move_player(direction_x=param1, direction_y=param2)
        elif type == WALL:
            valid = self.place_wall(x=param1, y=param2, orientation=param3, check=check)
        if not valid:
            return False
        self.graph.remove_edges_from(self.special_edges)
        self.next_turn()
        self.find_special_edges()
        self.graph.add_edges_from(self.special_edges)
        self.availables = self.possible_moves()
        return True

    def available_cells(self):
        p = self.players_loc[self.index]
        o = self.players_loc[1 - self.index]
        candidates = []
        for dx, dy in DELTA:
            if (dx != 0 or dy != 0) and (p[0] + dx != o[0] or p[1] + dy != o[1]):
                candidates.append((p[0] + dx, p[1] + dy))

        return filter(lambda node: self.has_edge(p, node), candidates)

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
        perp1 = np.array([vec[1], vec[0]])
        perp2 = - perp1
        for perp in (perp1, perp2):
            if self.has_edge(p2, p2 + perp):
                self.special_edges.append((tuple(p1), tuple(p2 + perp)))

    def has_edge(self, a, b):
        return self.graph.has_edge(tuple(a), tuple(b))

    def has_node(self, node):
        return self.graph.has_node(tuple(node))

    def make_move(self, action):
        check = not(hash(self) in MOVES and action in MOVES[hash(self)])
        self.play_game(*action, check)

    def is_terminal(self):
        return self.terminal

    def reward(self, parent, action):
        return self.scoring()

    def perform(self, action):
        self_copy = copy.deepcopy(self)
        self_copy.make_move(action)
        return self_copy

    def game_end(self):
        if self.is_terminal():
            return True, 1 - self.index
        else:
            return False, -1

    def get_current_player(self):
        return self.index

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
        distance_score = d2 - d1
        if self.index == 0:
            return distance_score
        else:
            return -distance_score

    def ttentry(self):
        return (tuple(self.players_loc[0]), tuple(self.players_loc[1]), tuple(self.horizontal_walls), tuple(self.vertical_walls), tuple(self.wall_counts), self.terminal, self.index, self.nplayer)

    def __hash__(self):
        return hash(self.ttentry())

    def ttrestore(self, entry):
        player_loc_0, player_loc_1, horizontal_walls, vertical_walls, wall_counts, terminal, index, nplayer = entry
        self.graph = nx.grid_2d_graph(self.size, self.size)
        self.players_loc[0] = np.array(player_loc_0)
        self.players_loc[1] = np.array(player_loc_1)
        self.horizontal_walls = set(horizontal_walls)
        self.vertical_walls = set(vertical_walls)

        for (x, y) in horizontal_walls:
            self.graph.remove_edges_from(Game.edges(x, y, HORIZONTAL))
        for (x, y) in vertical_walls:
            self.graph.remove_edges_from(Game.edges(x, y, VERTICAL))

        self.wall_counts = list(wall_counts)
        self.index = index
        self.terminal = terminal
        self.nplayer = nplayer
        self.find_special_edges()
        self.graph.add_edges_from(self.special_edges)

    def __eq__(self, other):
        return self.ttentry() == other.ttentry()
