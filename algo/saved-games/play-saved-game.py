import sys
import json
sys.path.insert(0,r'..\..')
from quoridor.game import Game
from quoridor.gui import GUI
import tkinter as tk
from datetime import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("id")
parser.add_argument("time")
args = parser.parse_args()

saved_game = json.load(open(f"{args.id}.json",'r'))

size = saved_game['size']
moves = saved_game['moves']
players = saved_game['players']
date = datetime.strptime(args.id, "%d-%m-%Y-%H-%M-%S")

print(f"Playing saved game played of date {date} between {players[0]} and {players[1]}...")

game = Game(size)
root = tk.Tk()

gui = GUI(root, game, [None, None])

def play_move():
    if moves == []:
        return
    
    move = moves.pop(0)
    game.make_move(move)
    gui.refresh()

    root.after(int(args.time) * 1000, play_move)

root.after(int(args.time) * 1000, play_move)
root.mainloop()
