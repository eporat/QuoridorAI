"""
The standard AI algorithm of easyAI is Negamax with alpha-beta pruning
and (optionnally), transposition tables.
"""

import pickle
import random
from easyAI.games.ThreeMusketeers import MOVES

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
    # if Negamax.moves % 100 == 0:
    #     print(Negamax.moves)

    Negamax.moves += 1

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
            if abs(score) >= 1000:
                return score - 0.01*depth
            return score


    if lookup != None:
        # Put the supposedly best move first in the list
        possible_moves = game.possible_moves()
        if len(possible_moves) == 0:
            print("TAMIR ERROR - NO POSSIBLE MOVES")
        if shuffle:
            random.shuffle(possible_moves)
        try:
            possible_moves.remove(lookup['move'])
            possible_moves = [lookup['move']] + possible_moves
        except:
            pass

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
        Negamax.moves = 0
        scoring = self.scoring if self.scoring else (
                       lambda g: g.scoring() ) # horrible hack

        self.alpha = negamax(game, self.depth, self.depth, scoring,
                     -self.win_score, +self.win_score, self.tt, self.shuffle)
        print(f"Number of moves (negamax) {Negamax.moves}")
        return game.ai_move

Negamax.moves = 0
