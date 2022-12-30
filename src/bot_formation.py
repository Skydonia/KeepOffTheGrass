import pandas as pd
from .actions import Move
from .logger import LOGGER
import operator
from scipy.optimize import linear_sum_assignment
import numpy as np
from .utils import get_distance_matrix, get_most_sided_tile_from_list


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

    def move_forward(self, bot):
        self.player.actions.append(Move(bot.units,
                                        bot,
                                        self.grid.loc[bot.x + self.player.optimal_move, bot.y]
                                        ))
        return


class ConquerFormation(BotFormation):
    def __init__(self, player, game):
        super().__init__(player, game)
        self.frontier = game.width // 2 + self.player.optimal_move
        self.__frontier_tiles = None
        self.__cost_matrix = None

    def get_frontier(self):
        self.__frontier_tiles = []
        ops = (operator.lt, operator.gt)[self.player.side == 'left']
        tiles = [bot for bot in self.bots if ops(bot.x, self.frontier)]
        self.__frontier_tiles = self.grid.loc[self.frontier].tolist()
        for tile in tiles:
            if ops(tile.x, self.__frontier_tiles[tile.y].x):
                self.__frontier_tiles[tile.y] = tile
        self.__frontier_tiles = [tile for tile in self.__frontier_tiles if tile.scrap_amount > 0]
        return self.__frontier_tiles

    @property
    def frontier_tiles(self):
        if self.__frontier_tiles is None:
            # self.__frontier_tiles = self.get_frontier()
            self.__frontier_tiles = self.grid.loc[self.frontier].tolist()
            self.__frontier_tiles = [tile for tile in self.__frontier_tiles if
                                     (tile.scrap_amount > 0) and (not tile.recycler)]
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
        only_moves = affectation_matrix[affectation_matrix['bot'] != affectation_matrix['target']]
        for i in only_moves.index:
            self.player.actions.append(Move(1, only_moves.loc[i]['bot'], only_moves.loc[i]['target']))
        # for bot in self.bots:
        #     self.move_forward(bot)


class PusherFormation(BotFormation):
    def __init__(self, player, game):
        super().__init__(player, game)
        self.frontier = (game.width // 2, game.width // 2 + self.player.optimal_move)[game.width % 2 == 1]

    def move(self):
        for bot in self.bots:
            ops = (operator.lt, operator.gt)[self.player.side == 'left']
            if ops(bot.x, self.frontier):
                self.move_forward(bot)
