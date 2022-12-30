import pandas as pd
from .actions import Move
from .logger import LOGGER
import operator
from scipy.optimize import linear_sum_assignment
import numpy as np
from .utils import get_distance_matrix


class BotFormation:
    def __init__(self, player, game):
        self.player = player
        self.tiles = game.tiles
        self.x_max = game.width - 1
        self.y_max = game.height - 1
        self.__grid = None

    @property
    def bots(self):
        return self.player.bots

    @property
    def unit_bots(self):
        return [bot for bot in self.bots for _ in range(bot.units)]

    @property
    def grid(self):
        if self.__grid is None:
            grid_dict = {}
            for tile in self.tiles:
                if tile.y not in grid_dict:
                    grid_dict[tile.y] = {tile.x: tile}
                    continue
                grid_dict[tile.y][tile.x] = tile
            self.__grid = pd.DataFrame(grid_dict)
            self.__grid.index.rename('x', inplace=True)
            self.__grid.columns.rename('y', inplace=True)
            self.__grid = self.__grid.sort_index()
            self.__grid = self.__grid.sort_index(axis=1)
        return self.__grid

    def move(self):
        return


class ConquerFormation(BotFormation):
    def __init__(self, player, game):
        super().__init__(player, game)
        self.frontier = (game.width // 2, game.width // 2 + 1)[game.width % 2 == 1]
        self.__frontier_tiles = None
        self.__cost_matrix = None

    @property
    def frontier_tiles(self):
        if self.__frontier_tiles is None:
            self.__frontier_tiles = self.grid.loc[self.frontier].tolist()
        return self.__frontier_tiles

    @property
    def cost_matrix(self):
        if self.__cost_matrix is None:
            self.__cost_matrix = get_distance_matrix(self.unit_bots, self.frontier_tiles)
        return self.__cost_matrix

    def affectation_matrix(self):
        row_ind, col_ind = linear_sum_assignment(self.cost_matrix)
        return pd.DataFrame({'bot': np.array([e[-1] for e in self.cost_matrix.index.tolist()])[row_ind],
                             'target': np.array([e[-1] for e in self.cost_matrix.columns.tolist()])[col_ind]})

    def move(self):
        affectation_matrix = self.affectation_matrix()
        for i in affectation_matrix.index:
            self.player.actions.append(Move(1, affectation_matrix.loc[i]['bot'], affectation_matrix.loc[i]['target']))
