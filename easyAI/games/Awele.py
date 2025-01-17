try:
    import numpy as np
except ImportError:
    print("Sorry, this example requires Numpy installed !")
    raise

from easyAI import TwoPlayersGame


class Awele(TwoPlayersGame):
    """
    Rules are as defined as in http://en.wikipedia.org/wiki/Oware
    with the additional rule that the game ends when then are 6 seeds
    left in the game.
    """

    def __init__(self, players):
        for i, player in enumerate(players):
            player.score = 0
            player.isstarved = False
            player.camp = i
        self.players = players
        
        # Initial configuration of the board.
        # holes are indexed by a,b,c,d...
        self.board = [4, 4, 4, 4, 4, 4,  
                      4, 4, 4, 4, 4, 4]  
                      
        self.nplayer = 1  # player 1 starts.

    def make_move(self, move):
        if move == "None":
            self.player.isstarved = True
            s = 6 * self.opponent.camp
            self.player.score += sum(self.board[s:s + 6])
            return

        move = 'abcdefghijkl'.index(move)

        pos = move
        for i in range(self.board[move]):  #DEAL
            pos = (pos + 1) % 12
            if pos == move:
                pos = (pos + 1) % 12
            self.board[pos] += 1

        self.board[move] = 0

        while ((pos / 6) == self.opponent.camp
               and (self.board[pos] in [2, 3])):  # TAKE
            self.player.score += self.board[pos]
            self.board[pos] = 0
            pos = (pos - 1) % 12

    def possible_moves(self):
        """
        A player must play any hole that contains enough seeds to
        'feed' the opponent. This no hole has this many seeds, any
        non-empty hole can be played.
        """

        if self.nplayer == 1:
            if max(self.board[:6]) == 0: return ['None']
            moves = [i for i in range(6) if (self.board[i] >= 6 - i)]
            if moves == []:
                moves = [i for i in range(6) if self.board[i] != 0]
        else:
            if max(self.board[6:]) == 0: return ['None']
            moves = [i for i in range(6,12) if (self.board[i] >= 12-i)]
            if moves == []:
                moves = [i for i in range(6, 12) if self.board[i] != 0]

        return ['abcdefghijkl'[u] for u in moves]

    def show(self):
        """ Prints the board, with the hole's respective letters """

        print("Score: %d / %d" % tuple(p.score for p in self.players))
        print('  '.join('lkjihg'))
        print(' '.join(["%02d" % i for i in self.board[-1:-7:-1]]))
        print(' '.join(["%02d" % i for i in self.board[:6]]))
        print('  '.join('abcdef'))

    def lose(self):
        return self.opponent.score > 24

    def is_terminal(self):
        return ( self.lose() or
                  sum(self.board) < 7 or
                  self.opponent.isstarved )


if __name__ == "__main__":
    # In what follows we setup the AI and launch a AI-vs-AI match.

    from easyAI import Human_Player, AI_Player, Negamax

    # this shows that the scoring can be defined in the AI algo, 
    # which enables 2 AIs with different scorings to play a match.
    scoring = lambda game: game.player.score - game.opponent.score
    ai = Negamax(6, scoring)
    game = Awele([AI_Player(ai), AI_Player(ai)])

    game.play()

    if game.player.score > game.opponent.score:
        print("Player %d wins." % game.nplayer)
    elif game.player.score < game.opponent.score:
        print("Player %d wins." % game.nopponent)
    else:
        print("Looks like we have a draw.")
