import sys
sys.path.append("../")
from MCTS.mcts import mcts
from game.game import *
from game.gui import *
import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk

game = Game(5)

for _ in range(10):
    root = tk.Tk()
    gui = GUI(root, game)
    m = mcts(timeLimit=5000)

    action = m.search(initialState=game)
    game.play(*action)

    root.mainloop()
