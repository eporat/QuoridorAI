from sys import argv
from gui import GUI
from game import Game
import tkinter as tk


def main():
    root = tk.Tk()
    game = Game(BOARD_SIZE)
    GUI(root, game)
    root.mainloop()


if __name__ == '__main__':
    BOARD_SIZE = int(argv[1])
    main()
