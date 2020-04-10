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
from easyAI import Negamax, TT
import networkx as nx

SIZE = 5
DEPTH = 1

class Population:
    def __init__(self, depth, size, tt_file_name=None, count=1, mutation_rate=1e-2, best_percent=0.2, gene_size=7):
        self.count = count
        self.genes = None
        self.mutation_rate = mutation_rate
        self.best_percent = best_percent
        self.depth = depth
        self.size = size # Board size
        self.gene_size = gene_size
        self.tt_file_name = tt_file_name

        try:
            self.tt = TT.fromfile(self.tt_file_name)
            print("Loaded TT")
        except Exception as e:
            print("TT could not be found in memory")
            self.tt = TT()



    def calculate(self, game):
        average_degrees = self.average_degrees(game) # +
        jump = self.jump(game) # +
        center = self.center(game) # 0
        side = self.side(game) # +
        wall = self.wall(game) # +
        dist_player = self.dist_between_players(game) # -
        dist = self.distance(game) # +
        # [ 2.17708616, 0.14143157, -0.39465167, 2.45134455, -1.29809957, -0.00416553, -0.38419192]
        return np.array([dist, wall, jump, side, average_degrees, center, dist_player])[:self.gene_size]

    def walking_moves(self, game):
        return len(game.available_cells())

    def average_degrees(self, game):
        # average of possible walking moves
        moves = list(game.available_cells())
        sum_degrees = 0
        for cell in moves:
            sum_degrees += game.graph.degree(tuple(cell))

        return sum_degrees/len(moves)

    def jump(self, game):
        for cell in game.available_cells():
            if game.distance(game.index, cell) == 2:
                return 1

        return 0

    def center(self, game):
        CENTER = np.array([game.size // 2, game.size // 2])
        d1 = game.distance(game.index, CENTER)
        d2 = game.distance(1 - game.index, CENTER)
        return (d1 - d2)

    def side(self, game):
        score = 0

        if abs(game.players_loc[game.index][1] - game.end_loc[game.index]) <= game.size // 2:
            score += 1

        if abs(game.players_loc[1 - game.index][1] - game.end_loc[1 - game.index]) <= game.size // 2:
            score -= 1

        return score

    def wall(self, game):
        return game.wall_counts[game.index] - game.wall_counts[1 - game.index]

    def dist_between_players(self, game):
        locs = game.players_loc
        p0_loc = locs[game.index]
        p1_loc = locs[1 - game.index]
        return np.abs(p0_loc-p1_loc).sum()

    def distance(self, game):
        con1 = nx.node_connected_component(game.graph, tuple(game.players_loc[0]))
        con1 = filter(lambda x: x[1] == game.size - 1, con1)
        d1 = min(nx.shortest_path_length(game.graph, tuple(game.players_loc[0]), node) for node in con1)
        con2 = nx.node_connected_component(game.graph, tuple(game.players_loc[1]))
        con2 = filter(lambda x: x[1] == 0, con2)
        d2 = min(nx.shortest_path_length(game.graph, tuple(game.players_loc[1]), node) for node in con2)
        distance_score =  d2 - d1

        if game.index == 0:
            return distance_score
        else:
            return -distance_score

    def scoring(self, gene):
        def gene_scoring(game):
            if game.players_loc[0][1] == game.size - 1:
                if game.index == 0:
                    return 1000
                else:
                    return -1000

            if game.players_loc[1][1] == 0:
                if game.index == 0:
                    return -1000
                else:
                    return 1000

            lookup = self.tt.lookup(game)

            if lookup is None:
                score = self.calculate(game)
                self.tt.store(game=game, score=score)
                return score @ gene

            return lookup['score'] @ gene

        return gene_scoring

    def mutate(self, gene):
        new_gene = gene.copy()
        for i in range(self.gene_size):
            if np.random.random() > 1 - self.mutation_rate:
                new_gene[i] = np.random.normal(0, 1)

        return new_gene

    def crossover(self, i, j):
        fit1 = self.fitness[i]
        fit2 = self.fitness[j]
        gene1 = self.genes[i]
        gene2 = self.genes[j]

        fit = (fit1 + 1e-3) / (fit1 + fit2 + 2e-3)
        chosen = np.random.choice(2, self.gene_size, p=[fit, 1-fit])
        new_gene = np.zeros(self.gene_size)
        new_gene[chosen == 0] = gene1[chosen == 0]
        new_gene[chosen == 1] = gene2[chosen == 1]
        return new_gene

    def calculate_fitnesses(self):
        pass

    def create(self):
        a = self.selection()
        b = self.selection()
        return self.mutate(self.crossover(a,b))

    def get_best(self):
        best_idx = np.argsort(self.prob)[int(-self.best_percent * len(self.prob)):]
        return self.genes[best_idx]

    def selection(self):
        return np.random.choice(a=range(self.count), p=self.prob)

    def game(self, player1, player2):
        players = [player1, player2]

        game = Game(self.size)
        moves = []
        index = 0

        while not game.is_terminal() and len(moves) < self.size*50:
            move = players[index](game)
            end = time.time()
            game.play_game(*move)
            moves.append(move)
            index = 1 - index

        if len(moves) == self.size*50:
            return 0
        if index == 1:
            return 1
        else:
            return 2

    def run_games(self, generations):
        for generation in range(generations):
            print(f"Generation: {generation}")
            if generation == 0:
                self.genes = np.random.normal(0,1,(self.count, self.gene_size))
            else:
                # selection
                new_genes = np.zeros((self.count, self.gene_size))
                best_genes = self.get_best()
                new_genes[:len(best_genes)] = best_genes
                for i in range(len(best_genes), self.count):
                    new_genes[i] = self.create()
                self.genes = new_genes

            self.fitness = np.zeros(self.count)
            # crossover
            self.players = [Negamax(self.depth, scoring=self.scoring(gene), tt=TT()) for gene in self.genes]

            num_games = self.count * self.count
            game_count = 0

            for i, gene1 in enumerate(self.genes):
                for j, gene2 in enumerate(self.genes):

                    if game_count % 10 == 0:
                        self.tt.tofile(self.tt_file_name)
                        print(f"Played game: {game_count} / {num_games}")


                    game_count += 1
                    if i == j:
                        continue

                    result = self.game(self.players[i],self.players[j])

                    if result == 0:
                        self.fitness[i] += 0.5
                        self.fitness[j] += 0.5

                    if result == 1:
                        self.fitness[i] += 1

                    if result == 2:
                        self.fitness[j] += 1

            self.prob = self.fitness / self.fitness.sum()

            idx = np.argmax(self.prob)
            best_gene = self.genes[idx]
            print(f"Best player: {best_gene}")
            print(f"Best fitness: {np.max(self.fitness)/(2*(self.count - 1))}")

            negamax = Negamax(self.depth, tt=TT())
            negamax_best = self.players[idx]

            score1 = self.game(negamax, negamax_best)
            print(f"When normal Negamax started: {score1}")
            score2 = self.game(negamax_best, negamax)
            print(f"When best player started: {score2}")

if __name__ == "__main__":

    # NOT SURE WHAT THE NAME IS
    population = Population(depth=DEPTH, size=SIZE, tt_file_name="genetic/tt_5.data", count=20, mutation_rate=0.05, best_percent=0.2, gene_size=7)
    population.run_games(10)
    # best_gene = [1.53276322, -0.31481973, 0.91032865, 0.10268689, 0.41397708, 0.93256447, 0.067119]
    # p1 = Negamax(5, scoring=population.scoring([1,0,0,0,0,0,0]), tt=TT())
    # p2 = Negamax(1, scoring=population.scoring(best_gene), tt=TT())
    # print(population.game(p1, p2))
    # print(population.game(p2, p1))
    population.tt.tofile(population.tt_file_name)
