import copy

import pandas as pd
from .actions import Move
from .logger import LOGGER
import operator
from scipy.optimize import linear_sum_assignment
import numpy as np
from .utils import get_distance_matrix, get_most_sided_tile_from_list
from .const import ME, OPP
from .frontier import Frontier


class BotFormation:
    def __init__(self, player, game):
        self.player = player
        self.tiles = game.tiles
        self.x_max = game.width - 1
        self.y_max = game.height - 1
        self.grid = game.grid

    @property
    def bots(self):
        return self.player.bots

    @property
    def unit_bots(self):
        return [bot for bot in self.bots for _ in range(bot.units)]

    def move(self):
        return

    def move_forward(self, bot):
        self.player.actions.append(Move(bot.units,
                                        bot,
                                        self.grid.loc[bot.x + self.player.optimal_move, bot.y]
                                        ))
        return

    def update(self, player, game):
        self.player = player
        self.tiles = game.tiles
        self.x_max = game.width - 1
        self.y_max = game.height - 1
        self.grid = game.grid


class ConquerFormation(BotFormation):
    def __init__(self, player, game):
        super().__init__(player, game)
        self.__frontier_tiles = None
        self.__cost_matrix = None
        self.frontier = copy.deepcopy(self.player.most_sided_bot.x) + self.player.optimal_move

    def update(self, player, game):
        super().update(player, game)
        self.__frontier_tiles = None
        self.__cost_matrix = None

    def get_frontier(self):
        new_frontier = []
        for t in self.__frontier_tiles:
            sided = self.grid.loc[t.x + self.player.optimal_move, t.y]
            if sided.units > 0 and sided.owner == ME:
                new_frontier.append(sided)
                continue
            new_frontier.append(t)
        return new_frontier

    @property
    def frontier_tiles(self):
        if self.__frontier_tiles is None:
            self.__frontier_tiles = self.grid.loc[self.frontier].tolist()
            self.__frontier_tiles = [tile for tile in self.__frontier_tiles if
                                     (tile.scrap_amount > 0) and (
                                         not tile.recycler) and (
                                         not self.grid.loc[tile.x + self.player.optimal_move, tile.y].recycler)]
            self.__frontier_tiles = self.get_frontier()
        return self.__frontier_tiles

    @property
    def cost_matrix(self):
        if self.__cost_matrix is None:
            self.__cost_matrix = get_distance_matrix(self.unit_bots, self.frontier_tiles)
            self.__cost_matrix = self.__cost_matrix ** 2
        return self.__cost_matrix

    def affectation_matrix(self):
        row_ind, col_ind = linear_sum_assignment(self.cost_matrix)
        return pd.DataFrame({'bot': np.array([e[-1] for e in self.cost_matrix.index.tolist()])[row_ind],
                             'target': np.array([e[-1] for e in self.cost_matrix.columns.tolist()])[col_ind]})

    def move(self):
        affectation_matrix = self.affectation_matrix()
        only_moves = affectation_matrix[affectation_matrix['bot'] != affectation_matrix['target']]
        frontier_secured = self.frontier_secured()
        LOGGER.append(f'MESSAGE secured ({[t.x for t in self.frontier_tiles]}): {frontier_secured}')
        if frontier_secured:
            self.frontier += 1
            self.__frontier_tiles = None
            frontier_secured = self.frontier_secured()
        for i in only_moves.index:
            bot = only_moves.loc[i]['bot']
            sided = self.grid.loc[bot.x + self.player.optimal_move, bot.y]
            if not frontier_secured and not (sided.units > 0 and sided.owner == OPP):
                self.player.actions.append(Move(1, bot, only_moves.loc[i]['target']))
        for bot in self.bots:
            sided = self.grid.loc[bot.x + self.player.optimal_move, bot.y]
            if not (sided.units > 0 and sided.owner == OPP):
                self.move_forward(bot)

    def frontier_secured(self):
        for tile in self.frontier_tiles:
            if tile.owner != ME and tile.scrap_amount > 0:
                return False
        return True
