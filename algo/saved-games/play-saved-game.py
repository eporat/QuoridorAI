import sys
sys.path.append("../../")
import json
from game.game import Game
from game.gui import GUI
import tkinter as tk
from sys import argv
from datetime import datetime


saved_game_id = argv[1]
saved_game = json.load(open(f"{saved_game_id}.json",'r'))

size = saved_game['size']
moves = saved_game['moves']
players = saved_game['players']
date = datetime.strptime(saved_game_id, "%d-%m-%Y-%H-%M-%S")

print(f"Playing saved game played of date {date} between {players[0]} and {players[1]}...")

game = Game(size)
root = tk.Tk()

gui = GUI(root, game)


def play_move():
    if moves == []:
        return
    
    move = moves.pop(0)
    game.make_move(move)
    gui.refresh()

    root.after(1000, play_move)

root.after(1000, play_move)
root.mainloop()
