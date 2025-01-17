import tkinter as tk
from functools import partial
from itertools import chain
from quoridor.game import Game, MOVEMENT, WALL, HORIZONTAL, VERTICAL
from datetime import datetime
from PIL import Image
import os
import time

def save_as_png(canvas,fileName):
    # save postscipt image 
    canvas.postscript(file = fileName + '.eps') 
    # use PIL to convert to PNG 
    img = Image.open(fileName + '.eps')
    path = fileName.split("/")
    img.save('/'.join(path[:-1]) + '/gif/' + path[-1] + '.png', 'png') 

class GUI:
    def __init__(self, root, game, players):
        now = datetime.now()
        self.date_time = now.strftime("%d-%m-%Y-%H-%M-%S")
        os.mkdir(f'saved-games/{self.date_time}')
        os.mkdir(f'saved-games/{self.date_time}/gif')
        self.root = root
        self.game = game
        self.players = players
        self.turn = 0

        self.canvas = tk.Canvas(self.root, width=500, height=500,
                                borderwidth=0, highlightthickness=0, background='gray')
        self.canvas.pack(side="top", fill="both", expand="true")

        self.CELL_SIZE = 500 / self.game.size
        self.rect = {}
        self.oval = {}
        self.click_horizontal = {}
        self.horizontal_walls = {}
        self.vertical_walls = {}

        self.click_vertical = {}
        self.click_vertical = {}
        self.player_colors = ['white', 'black']
        self.spacing = self.CELL_SIZE * 0.2

        for column in range(self.game.size):
            for row in range(self.game.size):
                x1 = self.spacing // 2 + column * self.CELL_SIZE
                y1 = self.spacing // 2 + row * self.CELL_SIZE
                x2 = x1 + self.CELL_SIZE - self.spacing
                y2 = y1 + self.CELL_SIZE - self.spacing
                self.rect[row, column] = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill='brown', tag='square')

        self.players_oval = [None, None]
        self.r = self.CELL_SIZE * 0.3

        for i, (x, y) in enumerate(self.game.players_loc):
            x = (x + 0.5) * self.CELL_SIZE
            y = (y + 0.5) * self.CELL_SIZE
            self.players_oval[i] = self.canvas.create_oval(
                x - self.r, y - self.r, x + self.r, y + self.r)

        for column in range(self.game.size - 1):
            for row in range(1, self.game.size):
                x1 = self.spacing // 2 + column * self.CELL_SIZE
                y1 = row * self.CELL_SIZE - self.spacing // 2
                x2 = x1 + self.CELL_SIZE - self.spacing
                y2 = y1 + self.spacing

                self.click_horizontal[row, column] = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill='', width=0, tag='click-area-horizontal')

        for column in range(1, self.game.size):
            for row in range(self.game.size - 1):
                x1 = column * self.CELL_SIZE - self.spacing // 2
                y1 = self.spacing // 2 + row * self.CELL_SIZE
                x2 = x1 + self.spacing
                y2 = y1 + self.CELL_SIZE - self.spacing

                self.click_vertical[row, column] = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill='', width=0, tag='click-area-vertical')

        self.refresh()
        for i, player in enumerate(self.players_oval):
            self.canvas.itemconfig(player, fill=self.player_colors[i])

        self.canvas.tag_bind('square', '<Button-1>', self.move)
        self.canvas.tag_bind('click-area-horizontal',
                             '<Button-1>', self.on_click_horizontal)
        self.canvas.tag_bind('click-area-vertical',
                             '<Button-1>', self.on_click_vertical)
        self.canvas.pack()

        self.root.after(100, self.play_game)

    def move(self, event):
        if self.game.terminal:
            return
        i = int(event.x // self.CELL_SIZE)
        j = int(event.y // self.CELL_SIZE)
        direction = self.game.direction(i, j)
        valid = self.game.play_game(MOVEMENT, *direction)
        self.refresh()
        if valid:
            self.root.after(10, self.play_game)

    def play_game(self):
        print("Game score", self.game.scoring())
        save_as_png(self.canvas, f"saved-games/{self.date_time}/{self.turn}")
        self.turn += 1
        player = self.players[self.game.index]
        if player == "Human" or player == None:
            return
        else:
            print("Thinking...", end=" ")
            move = player(self.game)
            self.game.play_game(*move)
            if hasattr(player, 'alpha'):
                print("predicted score: ", player.alpha)
            self.refresh()

            other_player = self.players[self.game.index]

            if other_player != "Human" and other_player != None:
                self.root.after(1000, self.play_game)


    def find_row_column_by_id(self, find_id):
        for (row, column), id in chain(self.click_horizontal.items(), self.click_vertical.items()):
            if id == find_id:
                return row, column

    def find_row_column(self, event):
        id_closest = event.widget.find_closest(event.x, event.y)[0]
        return self.find_row_column_by_id(id_closest)

    def add_horizontal_wall(self, row, column, check=True):
        if check and not self.game.play_game(WALL, column, row - 1, HORIZONTAL):
            return
        x1 = self.spacing // 2 + column * self.CELL_SIZE
        y1 = row * self.CELL_SIZE - self.spacing // 2
        x2 = x1 + self.CELL_SIZE + self.CELL_SIZE - self.spacing
        y2 = y1 + self.spacing
        rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill='orange')
        self.horizontal_walls[row, column] = rect
        return rect

    def on_click_horizontal(self, event):
        if self.game.terminal:
            return
        row, column = self.find_row_column(event)
        valid = self.add_horizontal_wall(row, column)
        self.refresh()
        if valid:
            self.root.after(10, self.play_game)


    def add_vertical_wall(self, row, column, check=True):
        if check and not self.game.play_game(WALL, column - 1, row, VERTICAL):
            return
        x1 = column * self.CELL_SIZE - self.spacing // 2
        y1 = self.spacing // 2 + row * self.CELL_SIZE
        x2 = x1 + self.spacing
        y2 = y1 + self.CELL_SIZE + self.CELL_SIZE - self.spacing
        rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill='orange')
        self.vertical_walls[row, column] = rect
        return rect

    def on_click_vertical(self, event):
        if self.game.terminal:
            return
        row, column = self.find_row_column(event)
        valid = self.add_vertical_wall(row, column)
        self.refresh()
        if valid:
            self.root.after(10, self.play_game)


    def refresh(self):
        for player, (x, y) in zip(self.players_oval, self.game.players_loc):
            x = (x + 0.5) * self.CELL_SIZE
            y = (y + 0.5) * self.CELL_SIZE
            self.canvas.coords(player, x - self.r, y -
                               self.r, x + self.r, y + self.r)

        for column in range(self.game.size):
            for row in range(self.game.size):
                self.canvas.itemconfig(self.rect[row, column], fill='brown')

        for x, y in self.game.vertical_walls:
            if (y, x + 1) not in self.vertical_walls:
                self.add_vertical_wall(y, x + 1, check=False)

        for x, y in self.game.horizontal_walls:
            if (y + 1, x) not in self.horizontal_walls:
                self.add_horizontal_wall(y + 1, x, check=False)

        if self.game.terminal:
            self.canvas.create_text(250, 250, fill="darkblue", font="Times 64 italic bold",
                                    text="Game Over!")
            return

        for x, y in self.game.available_cells():
            self.canvas.itemconfig(
                self.rect[y, x], fill=self.player_colors[self.game.index])
