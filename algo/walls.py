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
DEPTH1 = 2
DEPTH2 = 2
NUM_PLAYERS = 8
SIZE = 5
NUM_GAMES_EACH = 10 # has to be odd number

players_list = []
wall_scores = np.linspace(0,2, NUM_PLAYERS)


for i in range(NUM_PLAYERS):
    players_list.append(Negamax(DEPTH1))


#score_func consideres both player1 and player2!!! not only one player

while len(players_list) > 1:
    winners = [] # indexes of players which won
    curr_time = time.time()
    for i in range(0,len(players_list),2):
        count_white = 0
        for j in range(NUM_GAMES_EACH):
            game = Game(SIZE, wall_scores[i], wall_scores[i+1])
            moves = []
            index = 0
            players = [players_list[i], players_list[i+1]]

            while not game.is_terminal() and len(moves) < SIZE*15:
                move = players[index](game)
                game.play_game(*move)
                moves.append(move)
                index = 1 - index

            if index == 1:
                count_white += 1
        winners.append(i + 1 - count_white //(NUM_GAMES_EACH//2 + 1))
    players_list = [players_list[j] for j in winners]
    print(f"Passing to next round, after {time.time() - curr_time} seconds")
print(f"The winning player has wall_score={wall_scores[winners[0]]}")
