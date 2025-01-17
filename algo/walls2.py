import sys
sys.path.insert(0,'..')
from quoridor.game import Game
import time
from sys import argv
import argparse
from datetime import datetime
import json
import numpy as np
import create
from easyAI import Negamax, TT

# Constants. Notice that they are low.
DEPTH1 = 3
DEPTH2 = 3
NUM_PLAYERS = 6
SIZE = 5
NUM_GAMES_EACH = 15 # has to be odd number
MIN_WALL_SCORE_BOUND = 1.33
MAX_WALL_SCORE_BOUND = 1.335


players_list = []
wall_scores = np.linspace(MIN_WALL_SCORE_BOUND, MAX_WALL_SCORE_BOUND, NUM_PLAYERS)
player_scores = [0] * NUM_PLAYERS

for i in range(NUM_PLAYERS):
    players_list.append(Negamax(DEPTH1))


#score_func consideres both player1 and player2!!! not only one player
for i1, player1 in enumerate(players_list):
    for i2, player2 in enumerate(players_list):
        if player1 == player2 or i2 <= i1:
            continue
        curr_time = time.time()
        players = [Negamax(DEPTH1, tt=TT()), Negamax(DEPTH1, tt=TT())]
        for j in range(NUM_GAMES_EACH):
            game = Game(SIZE, wall_scores[i1], wall_scores[i2])
            moves = []
            index = 0

            while not game.is_terminal() and len(moves) < SIZE*15:
                move = players[index](game)
                game.play_game(*move)
                moves.append(move)
                index = 1 - index

            if index == 1:
                player_scores[i1] += 1
            else:
                player_scores[i2] += 1
        print(f"finished {NUM_GAMES_EACH} games between player{i1} and player{i2}")
        print(f"That took {time.time() - curr_time} seconds")


print(f"scores are {player_scores}")
best_player_index = np.argmax(player_scores)
print(f"best player is {best_player_index} with wall_score of {wall_scores[best_player_index]}")
