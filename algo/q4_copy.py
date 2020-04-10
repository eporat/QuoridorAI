import time
from datetime import datetime
import json
import numpy as np

import sys
sys.path.insert(0,'..')
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from itertools import product
import copy
import random

HORIZONTAL = 0
VERTICAL = 1

MOVEMENT = 0
WALL = 1

WALL_SCORE = 0 # Notice that wall score is 0 now!!!
DISTANCE_SCORE = 1

DELTA = [(-2, 0), (2, 0), (0, 2), (0, -2), (-1, 1), (-1, -1), (1, -1), (1, 1), (0, 1), (0, -1), (1, 0), (-1, 0)]


#contributed by mrfesol (Tomasz Wesolowski)

class HashTT:
    """
        Base Class for various types of hashes
    """

    def __init__(self):
        self.modulo = 1024 #default value

    def before(self, key):
        """
        Returns initial value of hash.
        It's also the place where you can initialize some auxiliary variables
        """
        return 1

    def after(self, key, hash):
        """
        Returns final value of hash
        """
        return hash

    def get_hash(self, key, depth = 0):
        """
        Recursively computes a hash
        """
        if depth == 0:
            ret_hash = self.before(key)
        if type(key) is int:
            return self.hash_int(key)
        if type(key) is str and len(key) <= 1:
            return self.hash_char(key)
        for v in list(key):
            ret_hash = self.join(ret_hash, self.get_hash(v, depth+1)) % self.modulo
        if depth == 0:
            ret_hash = self.after(key, ret_hash)
        return ret_hash

    def hash_int(self, number):
        """
        Returns hash for a number
        """
        return number

    def hash_char(self, string):
        """
        Returns hash for an one-letter string
        """
        return ord(string)

    def join(self, one, two):
        """
        Returns combined hash from two hashes
        one - existing (combined) hash so far
        two - hash of new element
        one = join(one, two)
        """
        return (one * two) % self.modulo

#contributed by mrfesol (Tomasz Wesolowski)
"""
Different types of hashes.
Try each to choose the one that cause the least collisions (you can check it by printing DictTT.num_collisions)
Also, you can easily create one of your own!

You can read more about these hash function on:
http://www.eternallyconfuzzled.com/tuts/algorithms/jsw_tut_hashing.aspx
"""

class SimpleHashTT(HashTT):
    """
    Surprisingly - very effective for strings
    """
    def join(self, one, two):
        return 101 * one  +  two

class XorHashTT(HashTT):
    def join(self, one, two):
        return one ^ two

class AddHashTT(HashTT):
    def join(self, one, two):
        return one  +  two

class RotateHashTT(HashTT):
    def join(self, one, two):
        return (one << 4) ^ (one >> 28) ^ two

class BernsteinHashTT(HashTT):
    def join(self, one, two):
        return 33 * one + two

class ShiftAndAddHashTT(HashTT):
    def join(self, one, two):
        return one ^ (one << 5) + (one >> 2) + two

class FNVHashTT(HashTT):
    def before(self, key):
        return 2166136261
    def join(self, one, two):
        return (one * 16777619) ^ two

class OneAtATimeTT(HashTT):
    def join(self, one, two):
        one += two
        one += (one << 10)
        return one ^ (one >> 6)

    def after(self, key, hash):
        hash += (hash << 3)
        hash ^= (hash >> 11)
        hash += (hash << 15)
        return hash

class JSWHashTT(HashTT):
    def before(self, key):
        return 16777551
    def join(self, one, two):
        return (one << 1 | one >> 31) ^ two

class ELFHashTT(HashTT):
    def before(self, key):
        self.g = 0
        return 0
    def join(self, one, two):
        one = (one << 4) + two;
        self.g = one & 0xf0000000;

        if self.g != 0:
            one ^= self.g >> 24

        one &= ~self.g;
        return (one << 1 | one >> 31) ^ two

class JenkinsHashTT(HashTT):
    """
    The most advanced hash function on the list.
    Way too many things going on to put something smart in short comment.
    """
    def mix(self, a, b, c):
        """
        Auxiliary function.
        """
        a -= b; a -= c; a ^= (c >> 13)
        b -= c; b -= a; b ^= (a << 8)
        c -= a; c -= b; c ^= (b >> 13)
        a -= b; a -= c; a ^= (c >> 12)
        b -= c; b -= a; b ^= (a << 16)
        c -= a; c -= b; c ^= (b >> 5)
        a -= b; a -= c; a ^= (c >> 3)
        b -= c; b -= a; b ^= (a << 10)
        c -= a; c -= b; c ^= (b >> 15)
        return a, b, c

    def before(self, key):
        self.a = self.b = 0x9e3779b9
        self.c = 0

    def get_hash(self, key, depth = 0):
        """
        Overridden.
        Just to create list of single elements to hash
        """
        if depth == 0:
            self.before(key)
        if type(key) is int:
            return [key]
        if type(key) is str and len(key) <= 1:
            return [key]
        tab = []
        for v in list(key):
            tab = tab + self.get_hash(v, depth+1)
        return self.compute_hash(tab)

    def compute_hash(self, tab):
        """
        Computes real hash
        """
        length = len(tab)
        cur = 0
        while length >= 12:
            self.a += (abs(tab[cur+0]) + (tab[cur+1] << 8) + (tab[cur+2] << 16) + (tab[cur+3] << 24))
            self.b += (tab[cur+4] + (tab[cur+5] << 8) + (tab[cur+6] << 16) + (tab[cur+7] << 24))
            self.c += (tab[cur+8] + (tab[cur+9] << 8) + (tab[cur+10] << 16) + (tab[cur+11] << 24))

            self.a, self.b, self.c = self.mix(self.a, self.b, self.c)

            cur += 12;
            length -= 12;

        self.c += len(tab);

        if(length == 11): self.c += (tab[cur+10] << 24);
        if(length == 10): self.c += (tab[9] << 16);
        if(length == 9): self.c += (tab[8] << 8);
        if(length == 8): self.b += (tab[7] << 24);
        if(length == 7): self.b += (tab[6] << 16);
        if(length == 6): self.b += (tab[5] << 8);
        if(length == 5): self.b += tab[4];
        if(length == 4): self.a += (tab[3] << 24);
        if(length == 3): self.a += (tab[2] << 16);
        if(length == 2): self.a += (tab[1] << 8);
        if(length == 1): self.a += tab[0];

        self.a, self.b, self.c = self.mix(self.a, self.b, self.c)

        return self.c

#contributed by mrfesol (Tomasz Wesolowski)

class HashTT:
    """
        Base Class for various types of hashes
    """

    def __init__(self):
        self.modulo = 1024 #default value

    def before(self, key):
        """
        Returns initial value of hash.
        It's also the place where you can initialize some auxiliary variables
        """
        return 1

    def after(self, key, hash):
        """
        Returns final value of hash
        """
        return hash

    def get_hash(self, key, depth = 0):
        """
        Recursively computes a hash
        """
        if depth == 0:
            ret_hash = self.before(key)
        if type(key) is int:
            return self.hash_int(key)
        if type(key) is str and len(key) <= 1:
            return self.hash_char(key)
        for v in list(key):
            ret_hash = self.join(ret_hash, self.get_hash(v, depth+1)) % self.modulo
        if depth == 0:
            ret_hash = self.after(key, ret_hash)
        return ret_hash

    def hash_int(self, number):
        """
        Returns hash for a number
        """
        return number

    def hash_char(self, string):
        """
        Returns hash for an one-letter string
        """
        return ord(string)

    def join(self, one, two):
        """
        Returns combined hash from two hashes
        one - existing (combined) hash so far
        two - hash of new element
        one = join(one, two)
        """
        return (one * two) % self.modulo

"""
This module implements transposition tables, which store positions
and moves to speed up the AI.
"""

import pickle

class TT:
    """
    A tranposition table made out of a Python dictionnary.
    It can only be used on games which have a method
    game.ttentry() -> string, or tuple

    Usage:

        >>> table = TT(DictTT(1024)) or table = TT() for default dictionary
        >>> ai = Negamax(8, scoring, tt = table) # boosted Negamax !
        >>> ai(some_game) # computes a move, fills the table
        >>> table.to_file('saved_tt.data') # maybe save for later ?

        >>> # later...
        >>> table = TT.fromfile('saved_tt.data')
        >>> ai = Negamax(8, scoring, tt = table) # boosted Negamax !

    Transposition tables can also be used as an AI (``AI_player(tt)``)
    but they must be exhaustive in this case: if they are asked for
    a position that isn't stored in the table, it will lead to an error.

    """

    def __init__(self, own_dict = None):
        self.d = own_dict if own_dict != None else dict()

    def lookup(self, game):
        """ Requests the entry in the table. Returns None if the
            entry has not been previously stored in the table. """
        return self.d.get(game.ttentry(), None)

    def __call__(self,game):
        """
        This method enables the transposition table to be used
        like an AI algorithm. However it will just break if it falls
        on some game state that is not in the table. Therefore it is a
        better option to use a mixed algorithm like

        >>> # negamax boosted with a transposition table !
        >>> Negamax(10, tt= my_dictTT)
        """
        return self.d[game.ttentry()]['move']

    def store(self, **data):
        """ Stores an entry into the table """
        entry = data.pop("game").ttentry()
        self.d[entry] = data

    def tofile(self, filename):
        """ Saves the transposition table to a file. Warning: the file
            can be big (~100Mo). """
        with open(filename, 'w+') as f:
            pickle.dump(self, f)

    @staticmethod
    def fromfile(self, filename):
        """ Loads a transposition table previously saved with
             ``TT.tofile`` """
        with open(filename, 'r') as f:
            pickle.load(self, filename)


from copy import deepcopy


class TwoPlayersGame:
    """
    Base class for... wait for it... two-players games !

    To define a new game, make a subclass of TwoPlayersGame, and define
    the following methods:

    - ``__init__(self, players, ...)`` : initialization of the game
    - ``possible_moves(self)`` : returns of all moves allowed
    - ``make_move(self, move)``: transforms the game according to the move
    - ``is_terminal(self)``: check whether the game has ended

    The following methods are optional:

    - ``show(self)`` : prints/displays the game
    - ``scoring``: gives a score to the current game (for the AI)
    - ``unmake_move(self, move)``: how to unmake a move (speeds up the AI)
    - ``ttentry(self)``: returns a string/tuple describing the game.

    The __init__ method *must* do the following actions:

    - Store ``players`` (which must be a list of two Players) into
      self.players
    - Tell which player plays first with ``self.nplayer = 1 # or 2``

    When defining ``possible_moves``, you must keep in mind that you
    are in the scope of the *current player*. More precisely, a
    subclass of TwoPlayersGame has the following attributes that
    indicate whose turn it is. These methods can be used but should not
    be overwritten:

    - ``self.player`` : the current player (e.g. ``Human_Player``)
    - ``self.opponent`` : the current Player's opponent (Player).
    - ``self.nplayer``: the number (1 or 2) of the current player.
    - ``self.nopponent``: the number (1 or 2) of the opponent.
    - ``self.nmove``: How many moves have been played so far ?

    For more, see the examples in the dedicated folder.

    Examples:
    ----------

    ::

        from easyAI import TwoPlayersGame, Human_Player

        class Sticks( TwoPlayersGame ):
            ''' In turn, the players remove one, two or three sticks from
                a pile. The player who removes the last stick loses '''

            def __init__(self, players):
                self.players = players
                self.pile = 20 # start with 20 sticks
                self.nplayer = 1 # player 1 starts
            def possible_moves(self): return ['1','2','3']
            def make_move(self,move): self.pile -= int(move)
            def is_terminal(self): return self.pile <= 0


        game = Sticks( [Human_Player(), Human_Player() ] )
        game.play()


    """

    def play(self, nmoves=1000, verbose=True):

        history = []

        if verbose:
            self.show()

        for self.nmove in range(1, nmoves+1):

            if self.is_terminal():
                break

            move = self.player.ask_move(self)
            history.append((deepcopy(self), move))
            self.make_move(move)

            if verbose:
                print( "\nMove #%d: player %d plays %s :"%(
                             self.nmove, self.nplayer, str(move)) )
                self.show()

            self.switch_player()

        history.append(deepcopy(self))

        return history

    @property
    def nopponent(self):
        return 2 if (self.nplayer == 1) else 1

    @property
    def player(self):
        return self.players[self.nplayer- 1]

    @property
    def opponent(self):
        return self.players[self.nopponent - 1]

    def switch_player(self):
        self.nplayer = self.nopponent

    def copy(self):
        return deepcopy(self)




class Game(TwoPlayersGame):
    def __init__(self, size, score_func0=None, score_func1=None, first_walls=None):
        self.score_func0 = score_func0
        self.score_func1 = score_func1
        self.first_walls = first_walls

        self.size = size
        self.nplayer = 1
        # self.players = players
        self.graph = nx.grid_2d_graph(self.size, self.size)
        self.players_loc = [np.array([self.size // 2, 0]),
                        np.array([self.size // 2, self.size - 1])]

        if first_walls is not None:
            self.wall_counts = [self.first_walls, self.size + 1]
        else:
            self.wall_counts = [self.size + 1, self.size + 1]
        self.vertical_walls = set()
        self.horizontal_walls = set()
        self.index = 0
        self.terminal = False
        self.special_edges = []
        self.end_loc = [self.size - 1, 0]
        self.availables = self.possible_moves()

    def possible_moves(self):
        if self.is_terminal():
            return []

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
        self.availables = self.possible_moves()

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
        if self.is_terminal():
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
        self.play_game(*action)

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
        wall_score = WALL_SCORE * (self.wall_counts[1] - self.wall_counts[0])
        distance_score = DISTANCE_SCORE * (d2 - d1)

        if self.score_func0 is not None and self.score_func1 is not None:
            v0 = self.score_func0 * self.wall_counts[0]
            v1 = self.score_func1 * self.wall_counts[1]
            if self.index == 0:
                return distance_score - (v1 - v0)
            else:
                return -distance_score + (v1 - v0)


        if self.index == 0:
            return distance_score - wall_score
        else:
            return -distance_score + wall_score

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


"""
The standard AI algorithm of easyAI is Negamax with alpha-beta pruning
and (optionnally), transposition tables.
"""

import pickle
import random

LOWERBOUND, EXACT, UPPERBOUND = -1,0,1
inf = float('infinity')

def negamax(game, depth, origDepth, scoring, alpha=+inf, beta=-inf,
             tt=None, shuffle=False):
    """
    This implements Negamax with transposition tables.
    This method is not meant to be used directly. See ``easyAI.Negamax``
    for an example of practical use.
    This function is implemented (almost) acccording to
    http://en.wikipedia.org/wiki/Negamax
    """


    #if tt != None:
        #tt.d.num_calcs += 1

    alphaOrig = alpha

    # Is there a transposition table and is this game in it ?
    lookup = None if (tt is None) else tt.lookup(game)

    if lookup != None:
        # The game has been visited in the past

        if lookup['depth'] >= depth:
            #tt.d.num_lookups += 1
            flag, value = lookup['flag'], lookup['value']
            if flag == EXACT:
                if depth == origDepth:
                    game.ai_move = lookup['move']
                return value
            elif flag == LOWERBOUND:
                alpha = max( alpha, value)
            elif flag == UPPERBOUND:
                beta = min( beta, value)

            if alpha >= beta:
                if depth == origDepth:
                    game.ai_move = lookup['move']
                return value




    if (depth == 0) or game.is_terminal():
        score = scoring(game)
        if score == 0:
            return score
        else:
            return  (score - 0.00001*depth*abs(score)/score)


    if lookup != None:
        # Put the supposedly best move first in the list
        possible_moves = game.possible_moves()
        if shuffle:
            random.shuffle(possible_moves)
        possible_moves.remove(lookup['move'])
        possible_moves = [lookup['move']] + possible_moves

    else:
        possible_moves = game.possible_moves()
        if shuffle:
            random.shuffle(possible_moves)

    state = game
    best_move = possible_moves[0]
    if depth == origDepth:
        state.ai_move = possible_moves[0]

    best_value = -inf
    unmake_move = hasattr(state, 'unmake_move')


    for move in possible_moves:

        if not unmake_move:
            game = state.copy() # re-initialize move

        game.make_move(move)
        game.switch_player()

        move_alpha = - negamax(game, depth-1, origDepth, scoring,
                               -beta, -alpha, tt)

        if unmake_move:
            game.switch_player()
            game.unmake_move(move)

        best_value = max( best_value,  move_alpha )
        if  alpha < move_alpha :
                alpha = move_alpha
                best_move = move
                if depth == origDepth:
                    state.ai_move = move
                if (alpha >= beta):
                    break

    if tt != None:

        assert best_move in possible_moves
        tt.store(game=state, depth=depth, value = best_value,
                 move= best_move,
                 flag = UPPERBOUND if (best_value <= alphaOrig) else (
                        LOWERBOUND if (best_value >= beta) else EXACT))

    return best_value


class Negamax:
    """
    This implements Negamax on steroids. The following example shows
    how to setup the AI and play a Connect Four game:

        >>> from easyAI.games import ConnectFour
        >>> from easyAI import Negamax, Human_Player, AI_Player
        >>> scoring = lambda game: -100 if game.lose() else 0
        >>> ai_algo = Negamax(8, scoring) # AI will think 8 turns in advance
        >>> game = ConnectFour([Human_Player(), AI_Player(ai_algo)])
        >>> game.play()

    Parameters
    -----------

    depth:
      How many moves in advance should the AI think ?
      (2 moves = 1 complete turn)

    scoring:
      A function f(game)-> score. If no scoring is provided
         and the game object has a ``scoring`` method it ill be used.

    win_score:
      Score above which the score means a win. This will be
        used to speed up computations if provided, but the AI will not
        differentiate quick defeats from long-fought ones (see next
        section).

    tt:
      A transposition table (a table storing game states and moves)
      scoring: can be none if the game that the AI will be given has a
      ``scoring`` method.

    Notes
    -----

    The score of a given game is given by

    >>> scoring(current_game) - 0.01*sign*current_depth

    for instance if a lose is -100 points, then losing after 4 moves
    will score -99.96 points but losing after 8 moves will be -99.92
    points. Thus, the AI will chose the move that leads to defeat in
    8 turns, which makes it more difficult for the (human) opponent.
    This will not always work if a ``win_score`` argument is provided.

    """


    def __init__(self, depth, scoring=None, win_score=+inf, tt=None, shuffle=False):
        self.scoring = scoring
        self.depth = depth
        self.tt = tt
        self.win_score= win_score
        self.shuffle = shuffle



    def __call__(self,game):
        """
        Returns the AI's best move given the current state of the game.
        """

        scoring = self.scoring if self.scoring else (
                       lambda g: g.scoring() ) # horrible hack

        self.alpha = negamax(game, self.depth, self.depth, scoring,
                     -self.win_score, +self.win_score, self.tt, self.shuffle)
        return game.ai_move


# Constants. Notice that they are low.
DEPTH1 = 1
DEPTH2 = 3
SIZE = 5
NUM_GAMES_EACH = 15 # has to be odd number
WALL_SCORE = 0

file = open("quoridor_smop_q4.txt", "w")

for depth1 in [1,2,3,4,5]:
    for depth2 in [1,2,3,4,5]:
        white_wins = 0
        draws = 0
        curr_time = time.time()
        player1 = Negamax(DEPTH1, tt=TT(), shuffle=False)
        player2 = Negamax(DEPTH2, tt=TT(), shuffle=True)
        players = [player1, player2]

        for _ in range(NUM_GAMES_EACH):

            game = Game(SIZE, WALL_SCORE, WALL_SCORE)
            moves = []
            index = 0

            while not game.is_terminal() and len(moves) < SIZE*15:
                move = players[index](game)
                game.play_game(*move)
                moves.append(move)
                index = 1 - index

            if len(moves) == SIZE*15:
                draws += 1
            elif index == 1:
                white_wins += 1

        file.write(f"board size is {SIZE} and player1 depth is {depth1} and player2 depth is {depth2}\n")
        file.write(f"that round took {time.time() - curr_time} seconds\n")
        file.write(f"white won {white_wins}/{NUM_GAMES_EACH}\n")
        file.write(f"black won {NUM_GAMES_EACH - white_wins - draws}/{NUM_GAMES_EACH}\n")
        file.write(f"number of draws is {draws}\n")


file.write("PLAYER 1 HAS SHUFFLE. PLAYER 2 DOES NOT")

for depth1 in [1,2,3,4,5]:
    for depth2 in [1,2,3,4,5]:
        white_wins = 0
        draws = 0
        curr_time = time.time()
        player1 = Negamax(DEPTH1, tt=TT(), shuffle=True)
        player2 = Negamax(DEPTH2, tt=TT(), shuffle=False)
        players = [player1, player2]

        for _ in range(NUM_GAMES_EACH):

            game = Game(SIZE, WALL_SCORE, WALL_SCORE)
            moves = []
            index = 0

            while not game.is_terminal() and len(moves) < SIZE*15:
                move = players[index](game)
                game.play_game(*move)
                moves.append(move)
                index = 1 - index

            if len(moves) == SIZE*15:
                draws += 1
            elif index == 1:
                white_wins += 1


        file.write(f"board size is {SIZE} and player1 depth is {depth1} and player2 depth is {depth2}\n")
        file.write(f"that round took {time.time() - curr_time} seconds\n")
        file.write(f"white won {white_wins}/{NUM_GAMES_EACH}\n")
        file.write(f"black won {NUM_GAMES_EACH - white_wins - draws}/{NUM_GAMES_EACH}\n")
        file.write(f"number of draws is {draws}\n")

file.close()
