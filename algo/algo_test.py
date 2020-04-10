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

#size, players = create.game()
TOTAL_GAMES = 1 # WHEN THATS DETERMINISTIC ITS NOT INTERESTING!!!
SIZES = [5,7,9]
DEPTH1 = 1
DEPTH2 = 3
MAX_DEPTH = 5
WALL_DIST = 7
SIZE = 5

depths = {
    3: [1,2,3,4,5],
    5: [1,2,3,4,5],
    7: [1,2,3],
    9: [1,2,3]
}

table1 = np.zeros((5,5))
table2 = np.zeros((5,5))
table3 = np.zeros((5,5)) # NOTICE THE SIZES!!!!

players_list = []

for i in range(MAX_DEPTH):
    # try:
    #     str = f'TT_folder/size{SIZE}/TT_depth{i + 1}/wall_score_0.0.data'
    #     print(str)
    #     tt_loaded = TT.fromfile(str)
    #     players_list.append(Negamax(i + 1, tt=tt_loaded))
    #     print("loaded")
    # except Exception as x:
    #     print(f"i dont have depth {i + 1} in memory")
    players_list.append(Negamax(i + 1, tt=TT()))


print("NO WALL RESTRICTION!!! DONT USE TT ")
for size in [5]:
    for depth1 in depths[size]:
        for depth2 in depths[size]:
                wins_white = 0
                draws = 0
                for i in range(TOTAL_GAMES):
                    players = [players_list[depth1 - 1], players_list[depth2 - 1]]

                    game = Game(size, wall_dist=[100, 100])
                    moves = []
                    index = 0

                    while not game.is_terminal() and len(moves) < size*50:
                        move = players[index](game)
                        end = time.time()
                        game.play_game(*move)
                        moves.append(move)
                        index = 1 - index

                    if len(moves) == size*50:
                        draws += 1
                        table1[depth1 - 1][depth2 - 1] = 0
                    elif index == 1:
                        table1[depth1 - 1][depth2 - 1] = 1
                        wins_white += 1
                    else:
                        table1[depth1 - 1][depth2 - 1] = -1


                print(f"size is {size}, player1 depth is {depth1}, player2 depth is {depth2}")
                print(f"white won {wins_white}/{TOTAL_GAMES}")
                print(f"black won {TOTAL_GAMES - wins_white - draws}/{TOTAL_GAMES}")
                print(f"number of draws is {draws}")


# for i, player in enumerate(players_list):
#     player.tt.tofile(f'TT_folder/size{SIZE}/TT_depth{i + 1}/wall_score_0.0.data')
'''
print("SECOND PLAYER HAS WALL DISTRICTION")
for size in [9]:
    for depth1 in depths[size]:
        for depth2 in depths[size]:
                wins_white = 0
                draws = 0
                for i in range(TOTAL_GAMES):
                    players = [players_list[depth1 - 1], players_list[depth2 - 1]]

                    game = Game(size, wall_dist=WALL_DIST, wall_dist_indexes=[1])
                    moves = []
                    index = 0

                    while not game.is_terminal() and len(moves) < size*50:
                        move = players[index](game)
                        end = time.time()
                        game.play_game(*move)
                        moves.append(move)
                        index = 1 - index


                    if len(moves) == size*50:
                        draws += 1
                        table2[depth1 - 1][depth2 - 1] = 0
                    elif index == 1:
                        wins_white += 1
                        table2[depth1 - 1][depth2 - 1] = 1
                    else:
                        table2[depth1 - 1][depth2 - 1] = -1


                print(f"size is {size}, player1 depth is {depth1}, player2 depth is {depth2}")
                print(f"white won {wins_white}/{TOTAL_GAMES}")
                print(f"black won {TOTAL_GAMES - wins_white - draws}/{TOTAL_GAMES}")
                print(f"number of draws is {draws}")


for i, player in enumerate(players_list):
    player.tt.tofile(f'TT_folder/size{SIZE}/TT_depth{i + 1}/no_wall_score.data')

print("BOTH PLAYERS HAS WALL DISTRICTION")
for size in [9]:
    for depth1 in depths[size]:
        for depth2 in depths[size]:
                wins_white = 0
                draws = 0
                for i in range(TOTAL_GAMES):
                    players = [players_list[depth1 - 1], players_list[depth2 - 1]]

                    game = Game(size, wall_dist=WALL_DIST, wall_dist_indexes=[0, 1])
                    moves = []
                    index = 0

                    while not game.is_terminal() and len(moves) < size*50:
                        move = players[index](game)
                        end = time.time()
                        game.play_game(*move)
                        moves.append(move)
                        index = 1 - index

                    if len(moves) == size*50:
                        draws += 1
                        table3[depth1 - 1][depth2 - 1] = 0
                    elif index == 1:
                        wins_white += 1
                        table3[depth1 - 1][depth2 - 1] = 1
                    else:
                        table3[depth1 - 1][depth2 - 1] = -1



                print(f"size is {size}, player1 depth is {depth1}, player2 depth is {depth2}")
                print(f"white won {wins_white}/{TOTAL_GAMES}")
                print(f"black won {TOTAL_GAMES - wins_white - draws}/{TOTAL_GAMES}")
                print(f"number of draws is {draws}")


for i, player in enumerate(players_list):
    player.tt.tofile(f'TT_folder/size{SIZE}/TT_depth{i + 1}/no_wall_score.data')
'''
print("first player has wall distriction")
print(table1)
'''
print("second player has wall distriction")
print(table2)
print("both players has wall distriction")
print(table3)
'''
print(f"wall dist is {WALL_DIST}")
