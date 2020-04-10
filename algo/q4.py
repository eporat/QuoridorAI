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
DEPTH1 = 1
DEPTH2 = 3
SIZE = 5
NUM_GAMES_EACH = 45 # has to be odd number
WALL_SCORE = 0 # NOTICE THAT!!!!!!!!!!!!!!!!!!!!!!

players_list_no_shuffle = [Negamax(i + 1, tt=TT(), shuffle=False) for i in range(5)]
players_list_yes_shuffle = [Negamax(i + 1, tt=TT(), shuffle=True) for i in range(5)]


for depth1 in [1,2,3,4,5]:
    for depth2 in [1,2,3,4,5]:
        white_wins = 0
        draws = 0
        curr_time = time.time()
        players = [players_list_no_shuffle[depth1 - 1], players_list_yes_shuffle[depth2 - 1]]

        for _ in range(NUM_GAMES_EACH):

            game = Game(SIZE, wall_scores=[WALL_SCORE, WALL_SCORE])
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

        print(f"board size is {SIZE} and player1 depth is {depth1} and player2 depth is {depth2}")
        print(f"that round took {time.time() - curr_time} seconds")
        print(f"white won {white_wins}/{NUM_GAMES_EACH}")
        print(f"black won {NUM_GAMES_EACH - white_wins - draws}/{NUM_GAMES_EACH}")
        print(f"number of draws is {draws}")


for depth1 in [1,2,3,4,5]:
    for depth2 in [1,2,3,4,5]:
        white_wins = 0
        draws = 0
        curr_time = time.time()

        players = [players_list_no_shuffle[depth1 - 1], players_list_yes_shuffle[depth2 - 1]]


        for _ in range(NUM_GAMES_EACH):

            game = Game(SIZE, wall_scores=[WALL_SCORE, WALL_SCORE])
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

        print(f"board size is {SIZE} and player1 depth is {depth1} and player2 depth is {depth2}")
        print("PLAYER 1 HAS SHUFFLE. PLAYER 2 DOES NOT")
        print(f"that round took {time.time() - curr_time} seconds")
        print(f"white won {white_wins}/{NUM_GAMES_EACH}")
        print(f"black won {NUM_GAMES_EACH - white_wins - draws}/{NUM_GAMES_EACH}")
        print(f"number of draws is {draws}")
