import sys
sys.path.insert(0,'..')
from quoridor.game import Game
from mcts.mcts_pure import MCTSPlayer
from easyAI import Negamax, TT
from tqdm import tqdm

n_games = 10
tt = TT()
offset = 100
max_exp = 10
depth = 3

def f(offset, max_exp):
    if max_exp == 0:
        return offset

    for i in range(max_exp + 1):
        n_playout = offset + 2 ** i
        print(f"Number of playouts {n_playout}")

        draws = 0
        wins = [0,0]

        player1 = MCTSPlayer(n_playout=n_playout, win_score=100)
        player2 = Negamax(depth=depth, tt=tt)
        players = [player1, player2]
        game = Game(9)
        while not game.is_terminal():
            move = players[game.index](game)
            game.make_move(move)
            

        end, player = game.game_end()
        if end:
            wins[player] += 1
            if player == 0:
                return min(n_playout, f(offset + 2 ** (i - 1) + 1, i - 1))
    return 10000000
print(f(offset, 10))
