import sys
sys.path.insert(0,'..')
from gui import GUI
from quoridor.game import Game
from argparse import ArgumentParser
import create
from easyAI import TT
import cProfile
import tkinter as tk


def main(size, game, players):
    root = tk.Tk()
    GUI(root, game, players)
    root.mainloop()


if __name__ == '__main__':
    size, players = create.game()
    game = Game(size)
    main(size, game, players)
