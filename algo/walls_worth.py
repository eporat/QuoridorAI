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

DEPTH = 3
SIZE = 5

pop = Population(depth=DEPTH, size=SIZE, tt_file_name="genetic/size5/walls_worth.data", count=20, mutation_rate=0.05, gene_size=2)
pop.run_games(100)
