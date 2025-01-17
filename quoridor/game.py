import sys
sys.path.insert(0,'..')
import igraph as ig
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from itertools import product
import copy
import random
from easyAI import TwoPlayersGame
import traceback

HORIZONTAL = 0
VERTICAL = 1

MOVEMENT = 0
WALL = 1

WALL_SCORE = 0 # Notice that wall score is 0 now!!!
DISTANCE_SCORE = 1


DELTA = [[(0, 2), (-1, 1), (1, 1), (0, 1), (-2, 0), (2, 0), (-1, -1), (1, -1), (1, 0), (-1, 0), (0, -1), (0, -2)],\
         [(0, -2), (-1,-1), (1,-1), (0,-1), (-2, 0), (2, 0), (-1, 1), (1,  1),  (1, 0), (-1, 0), (0, 1), (0, 2)]]
POSSIBLE_MOVES = {}

graphs = {
    3: nx.grid_2d_graph(3, 3),
    5: nx.grid_2d_graph(5, 5),
    7: nx.grid_2d_graph(7, 7),
    9: nx.grid_2d_graph(9, 9)
}


class Game(TwoPlayersGame):
    def __init__(self, size, wall_counts=None, wall_dist=[100,100]):
        self.wall_dist = wall_dist
        self.size = size
        self.wall_counts = [self.size + 1, self.size + 1]

        if wall_counts:
            self.wall_counts = wall_counts
        self.nplayer = 1
        # self.players = players
        graph = graphs[self.size]
        self.graph = ig.Graph(directed=False)
        self.graph.add_vertices(list(map(self.node_id, graph.nodes())))
        self.graph_add(graph.edges())     
        self.players_loc = [np.array([self.size // 2, 0]),
                        np.array([self.size // 2, self.size - 1])]

        self.vertical_walls = set()
        self.horizontal_walls = set()
        self.index = 0
        self.terminal = False
        self.special_edges = []
        self.end_loc = [self.size - 1, 0]
        self.availables = self.possible_moves()

    def node_id(self, node):
        return node[0] + node[1] * self.size

    def edge_id(self, edge):
        return (self.node_id(edge[0]), self.node_id(edge[1]))

    def distance(self, index, loc):
        return abs(self.players_loc[index][0] - loc[0]) + abs(self.players_loc[index][1] - loc[1])

    def possible_moves(self):
        if self.is_terminal():
            return []
        
        if hash(self.ttentry()) in POSSIBLE_MOVES:
            return POSSIBLE_MOVES[hash(self.ttentry())]

        actions = []
        p = self.players_loc[self.index]
        o = self.players_loc[1 - self.index]

        for cell in self.available_cells():
            actions.append((MOVEMENT, cell[0] - p[0], cell[1] - p[1]))

        if self.wall_counts[self.index] > 0:
            locations = [cell for cell in product(range(self.size - 1), range(self.size - 1)) if \
                min(abs(cell[0] - o[0]) + abs(cell[1] - o[1]), abs(cell[0] - p[0]) + abs(cell[1] - p[1])) <= self.wall_dist[self.index]]

            for x, y in locations:
                if self.is_valid_vertical(x,y):
                    actions.append((WALL, x, y, VERTICAL))

                if self.is_valid_horizontal(x,y):
                    actions.append((WALL, x, y, HORIZONTAL))

        #random.shuffle(actions) # exists already in negamax player!
        # The actions are sorted in a way that moves are first and walls are seconds
        # the moves are ordered by jumping moves and then normal moves

        POSSIBLE_MOVES[hash(self.ttentry())] = actions
        return actions

    def edges(self, x, y, orientation):
        if orientation == HORIZONTAL:
            return [((x, y), (x, y + 1)), ((x + 1, y), (x + 1, y + 1))]
        elif orientation == VERTICAL:
            return [((x, y), (x + 1, y)), ((x, y + 1), (x + 1, y + 1))]

    def is_valid_horizontal(self, x, y):
        if (x, y) in self.vertical_walls:
            return
        edges = self.edges(x, y, HORIZONTAL)
        if (x, y) in self.horizontal_walls or (x - 1, y) in self.horizontal_walls or (x + 1, y) in self.horizontal_walls:
            return

        if not all(self.has_edge(*edge) for edge in edges):
            return

        self.graph_remove(edges)
        connected = self.check_connected()
        self.graph_add(edges)

        if not connected:
            return False

        return edges

    def is_valid_vertical(self, x, y):
        if (x, y) in self.horizontal_walls:
            return
        edges = self.edges(x, y, VERTICAL)
        if (x, y) in self.vertical_walls or (x, y - 1) in self.vertical_walls or (x, y + 1) in self.vertical_walls:
            return
        if not all(self.has_edge(*edge) for edge in edges):
            return

        self.graph_remove(edges)
        connected = self.check_connected()
        self.graph_add(edges)

        if not connected:
            return False

        return edges

    def place_horizontal(self, x, y, check=True):
        if not check:
            edges = self.edges(x, y, HORIZONTAL)
        else:
            edges = self.is_valid_horizontal(x, y)
            if not edges:
                return
        self.graph_remove(edges)
        self.horizontal_walls.add((x,y))
        return edges

    def place_vertical(self, x, y, check=True):
        if not check:
            edges = self.edges(x, y, VERTICAL)
        else:
            edges = self.is_valid_vertical(x, y)
            if not edges:
                return
        self.graph_remove(edges)
        self.vertical_walls.add((x,y))
        return edges

    def unmake_move(self, move):
        if move[0] == MOVEMENT:
            self.players_loc[1 - self.index][0] -= move[1]
            self.players_loc[1 - self.index][1] -= move[2]
            self.terminal = self.players_loc[1 - self.index][1] == self.end_loc[1 - self.index]
    
        elif move[0] == WALL:
            self.graph_add(self.edges(move[1], move[2], move[3]))

            if move[3] == HORIZONTAL:
                self.horizontal_walls.remove((move[1], move[2]))
            elif move[3] == VERTICAL:
                self.vertical_walls.remove((move[1], move[2]))
    
            self.wall_counts[1 - self.index] += 1
    
        self.graph_remove(self.special_edges)
        self.next_turn()
        self.find_special_edges()
        self.graph_add(self.special_edges)
        # self.availables = self.possible_moves()

    def place_wall(self, x, y, orientation, check=True):
        if not self.wall_counts[self.index]:
            return False
        if x == self.size - 1 or y == self.size - 1:
            return False
        if orientation == HORIZONTAL:
            edges = self.place_horizontal(x, y, check=check)
        elif orientation == VERTICAL:
            edges = self.place_vertical(x, y, check=check)
        if not edges:
            return False
        self.wall_counts[self.index] -= 1
        return True

    def path_length(self, a, b):
        paths = self.graph.shortest_paths(source=self.node_id(a), target=self.node_id(b))
        return min(paths, key=lambda x:x[0])[0]

    def check_connected(self):
        # Make sure there are still ways to reach the end
        self.graph_remove(self.special_edges)
        connected = min(self.graph.shortest_paths_dijkstra(self.node_id(self.players_loc[0]), [self.node_id((x,self.size-1)) for x in range(self.size)])[0]) < self.size * self.size
        if not connected:
            self.graph_add(self.special_edges)
            return False

        connected = min(self.graph.shortest_paths_dijkstra(self.node_id(self.players_loc[1]), [self.node_id((x,0)) for x in range(self.size)])[0]) < self.size * self.size
        self.graph_add(self.special_edges)
        return connected

    def move_player(self, direction_x, direction_y, check=True):
        direction = np.array([direction_x, direction_y])
        p = self.players_loc[self.index]
        if check and not self.has_edge(p, p + direction):
            return False
        self.players_loc[self.index] += direction
        if p[1] == (1 - self.size) * (self.index - 1):
            self.terminal = True
        return True

    def direction(self, i, j):
        return i - self.players_loc[self.index][0], j - self.players_loc[self.index][1]

    def next_turn(self):
        self.index = 1 - self.index

    def play_game(self, type, param1, param2=None, param3=None, check=True):
        if self.is_terminal():
            return
        if type == MOVEMENT:
            valid = self.move_player(direction_x=param1, direction_y=param2, check=check)
        elif type == WALL:
            valid = self.place_wall(x=param1, y=param2, orientation=param3, check=check)
        if not valid:
            return False
        self.graph_remove(self.special_edges)
        self.next_turn()
        self.find_special_edges()
        self.graph_add(self.special_edges)
        if check:
            self.availables = self.possible_moves()
        return True

    def available_cells(self):
        p = self.players_loc[self.index]
        o = self.players_loc[1 - self.index]
        candidates = []
        for dx, dy in DELTA[self.index]:
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
        if a[0] < 0 or a[1] < 0 or b[0] < 0 or b[1] < 0 or a[0] > self.size - 1 or a[1] > self.size - 1 or b[0] > self.size - 1 or b[1] > self.size - 1:
            return False

        return self.graph.are_connected(self.node_id(a), self.node_id(b))

    def make_move(self, action, check=True):
        self.play_game(*action, check=check)

    def is_terminal(self):
        return self.terminal

    def reward(self, parent, action):
        return self.scoring()

    def perform(self, action):
        self_copy = copy.deepcopy(self)
        self_copy.make_move(action, check=False)
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
    
        d1 = min(self.graph.shortest_paths_dijkstra(self.node_id(self.players_loc[0]), [self.node_id((x,self.size-1)) for x in range(self.size)])[0]) 
        d2 = min(self.graph.shortest_paths_dijkstra(self.node_id(self.players_loc[1]), [self.node_id((x,0)) for x in range(self.size)])[0])
        distance_score = d2 - d1

        if self.index == 0:
            return distance_score
        else:
            return -distance_score

    def ttentry(self):
        return (tuple(self.players_loc[0]), tuple(self.players_loc[1]), tuple(self.horizontal_walls), tuple(self.vertical_walls), tuple(self.wall_counts), self.terminal, self.index, self.nplayer)

    def __hash__(self):
        return hash(self.ttentry())

    def move_score(self, move):
        self.make_move(move, check=False)
        score = self.scoring()
        self.unmake_move(move)
        return score
    # def ttrestore(self, entry):
    #     player_loc_0, player_loc_1, horizontal_walls, vertical_walls, wall_counts, terminal, index, nplayer = entry
    #     self.graph = nx.grid_2d_graph(self.size, self.size)
    #     self.players_loc[0] = np.array(player_loc_0)
    #     self.players_loc[1] = np.array(player_loc_1)
    #     self.horizontal_walls = set(horizontal_walls)
    #     self.vertical_walls = set(vertical_walls)

    #     for (x, y) in horizontal_walls:
    #         self.graph.remove_edges_from(self.edges(x, y, HORIZONTAL))
    #     for (x, y) in vertical_walls:
    #         self.graph.remove_edges_from(self.edges(x, y, VERTICAL))

    #     self.wall_counts = list(wall_counts)
    #     self.index = index
    #     self.terminal = terminal
    #     self.nplayer = nplayer
    #     self.find_special_edges()
    #     self.graph.add_edges_from(self.special_edges)
    #     self.graph_add(self.special_edges)

    def __eq__(self, other):
        return self.ttentry() == other.ttentry()

    def graph_add(self, edges):
        if len(edges):
            self.graph.add_edges(list(map(self.edge_id, edges)))        

    def graph_remove(self, edges):
        if len(edges):
            self.graph.delete_edges(list(map(self.edge_id, edges)))