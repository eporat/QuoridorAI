import sys
sys.path.insert(0,'..')
from quoridor.gui import GUI
from quoridor.game import Game
from argparse import ArgumentParser
import create
from easyAI import TT
import cProfile
import tkinter as tk
from genetic import *

DEPTH = 1
SIZE = 5

player = create.Human()
pop = Population(DEPTH, SIZE)
#gene = [1.53276322, -0.31481973, 0.91032865, 0.10268689, 0.41397708, 0.93256447, 0.067119]
#gene = [2.17708616, 0.14143157, -0.39465167, 2.45134455, -1.29809957, 1.35924934, 0.1645196]
#gene = [ 2.17708616, 0.14143157, -0.39465167, 2.45134455, -1.29809957, -0.00416553, -0.38419192]
gene = [2.17708616, 0.44166281, -0.39465167, 0.65901557, -1.29809957, -0.00416553, -0.38419192]
# gene = [ 2.17708616, 0.14143157, -0.39465167, 0.70410026, -1.29809957, -0.00416553, -0.38419192]
negamax_good = Negamax(depth=DEPTH, scoring=pop.scoring(gene), tt=TT())
gene = [1, 0, 0, 0, 0, 0, 0]
negamax_bad = Negamax(depth=1, scoring=pop.scoring(gene), tt=TT())
def main(size, game, players):
    root = tk.Tk()
    GUI(root, game, players)
    root.mainloop()

if __name__ == '__main__':
    game = Game(SIZE)
    #main(SIZE, game, [negamax_good, negamax_bad])
    main(SIZE, game, [Negamax(depth=5, tt=TT()), Negamax(depth=2, tt=TT())])
