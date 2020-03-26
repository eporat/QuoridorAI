import sys
sys.path.append("../")
from game.game import *
from easyAI import Negamax, NonRecursiveNegamax, DUAL, SSS
import time
from sys import argv
import argparse
from datetime import datetime
import json
import numpy as np


types = {
    'Negamax': Negamax,
    'NonRecursiveNegamax': NonRecursiveNegamax,
    'DUAL': DUAL,
    'SSS': SSS
}

now = datetime.now()

parser = argparse.ArgumentParser()
parser.add_argument("size")
parser.add_argument("type_1")
parser.add_argument("depth_1")
parser.add_argument("type_2")
parser.add_argument("depth_2")

args = parser.parse_args()
size = int(args.size)
type_1 = args.type_1
type_2 = args.type_2
depth_1 = int(args.depth_1)
depth_2 = int(args.depth_2)

players = [types[type_1](depth=depth_1, win_score=100), 
           types[type_2](depth=depth_2, win_score=100)]

game = Game(size)
moves = []
index = 0

while not game.is_over():
    print("Playing move... ", end="")
    move = players[index](game)
    print(move)
    game.play_game(*move)
    moves.append(move)
    index = 1 - index

saved_game = dict()
saved_game['size'] = size
saved_game['players'] = [f"{type_1}-{depth_1}", f"{type_2}-{depth_2}"]
saved_game['moves'] = moves
date_time = now.strftime("%d-%m-%Y-%H-%M-%S")

def convert(o):
    if isinstance(o, np.int32): return int(o)  
    else: return o

with open(f'saved-games/{date_time}.json', 'w+') as f:
    json.dump(saved_game, f, default=convert, indent=2)