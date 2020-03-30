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

now = datetime.now()

size, players = create.game()

game = Game(size)
moves = []
index = 0

while not game.is_terminal():
    print("Playing move... ", end="")
    start = time.time()
    move = players[index](game)
    print(move)
    end = time.time()
    print(f'{end - start} seconds elapsed')
    game.play_game(*move)
    moves.append(move)
    index = 1 - index

saved_game = dict()
saved_game['size'] = size
saved_game['players'] = []

for player in players:
    saved_game['players'].append(f"{type(player).__name__}")
    for attr in set(dir(player)) - set(dir(object)) - set(['alpha', 'win_score']):
        if type(getattr(player, attr)) is int:
            saved_game['players'][-1] += f'-{attr}-{getattr(player, attr)}'

saved_game['moves'] = moves
date_time = now.strftime("%d-%m-%Y-%H-%M-%S")

def convert(o):
    if isinstance(o, np.int32): return int(o)  
    else: return o

with open(f'saved-games/{date_time}.json', 'w+') as f:
    json.dump(saved_game, f, default=convert)