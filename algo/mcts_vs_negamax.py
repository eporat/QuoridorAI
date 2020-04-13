import sys
sys.path.insert(0,'..')
from quoridor.game import Game
from mcts.mcts_pure import MCTSPlayer
from easyAI import Negamax, TT

game = Game(5)
player1 = MCTSPlayer(n_playout=1000, win_score=100)
player2 = Negamax(depth=1, tt=TT())
players = [player1, player2]

while not game.is_terminal():
    move = players[game.index](game)
    game.make_move(move)
    
print(game.game_end()[1])