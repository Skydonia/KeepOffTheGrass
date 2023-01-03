import copy

import pandas as pd
from .logger import LOGGER
import operator
from scipy.optimize import linear_sum_assignment
import numpy as np
from .utils import get_distance_matrix, get_most_sided_tile_from_list
from .const import ME, OPP, NONE
from .frontier import Frontier
from .actions import Move, Spawn
from datetime import datetime


class BotFormation:
    def __init__(self, player, game):
        self.player = player
        self.game = game

    @property
    def grid(self):
        return self.game.grid

    @property
    def x_max(self):
        return self.game.width - 1

    @property
    def y_max(self):
        return self.game.height - 1

    @property
    def tiles(self):
        return self.game.tiles

    @property
    def bots(self):
        return self.player.bots

    @property
    def unit_bots(self):
        return [bot for bot in self.bots for _ in range(bot.units)]

    def move(self):
        return

    def move_forward(self, bot):
        x = max(bot.x + self.player.optimal_move, 0)
        if self.player.side == 'left':
            x = min(bot.x + self.player.optimal_move, self.x_max)
        self.player.actions.append(Move(bot.units,
                                        bot,
                                        self.grid.loc[x, bot.y]
                                        ))
        return

    def update(self, player, game):
        self.player = player
        self.game = game


class ConquerFormation(BotFormation):
    def __init__(self, player, game):
        super().__init__(player, game)
        self.unlock = False
        self.frontier = Frontier(self.game)
        self.__cost_matrix = None

    def update(self, player, game):
        super().update(player, game)
        self.__cost_matrix = None
        self.frontier.update(self.game)
        self.frontier.push()

    @property
    def cost_matrix(self):
        if self.__cost_matrix is None:
            self.__cost_matrix = get_distance_matrix(self.unit_bots, self.frontier.tiles)
            self.__cost_matrix = self.__cost_matrix ** 2
        return self.__cost_matrix

    def affectation_matrix(self):
        row_ind, col_ind = linear_sum_assignment(self.cost_matrix)
        return pd.DataFrame({'bot': np.array([e[-1] for e in self.cost_matrix.index.tolist()])[row_ind],
                             'target': np.array([e[-1] for e in self.cost_matrix.columns.tolist()])[col_ind]})

    def move(self):
        affectation_matrix = self.affectation_matrix()
        only_moves = affectation_matrix[affectation_matrix['bot'] != affectation_matrix['target']]
        LOGGER.append(f'MESSAGE Frontier {[t.x for t in self.frontier.tiles]}')
        for i in only_moves.index:
            bot = only_moves.loc[i]['bot']
            if self.can_move(bot):
                self.player.actions.append(Move(1, bot, only_moves.loc[i]['target']))
        for bot in self.bots:
            if self.can_move(bot) or self.unlock:
                self.move_forward(bot)

    def can_move(self, bot):
        x = max(bot.x + self.player.optimal_move, 0)
        _x = min(bot.x - self.player.optimal_move, self.x_max)
        if self.player.side == 'left':
            x = min(bot.x + self.player.optimal_move, self.x_max)
            _x = max(bot.x - self.player.optimal_move, 0)
        backup = self.grid.loc[_x, bot.y]
        sided = self.grid.loc[x, bot.y]
        upper = self.grid.loc[bot.x, max(bot.y - 1, 0)]
        lower = self.grid.loc[bot.x, min(bot.y + 1, self.y_max)]
        if backup.units > 0 and backup.owner == ME:
            return True
        if (
                sided.units > 0 and sided.owner == OPP) or (
                upper.units > 0 and upper.owner == OPP) or (
                lower.units > 0 and lower.owner == OPP):
            return False
        return True


class CombatFormation(BotFormation):
    def __init__(self, player, game, isle):
        super().__init__(player, game)
        self.isle = isle
        self.__cost_matrix = None

    def update(self, player, game):
        super().update(player, game)
        self.__cost_matrix = None
        for isle in self.game.isles:
            if isle.id == self.isle.id:
                self.isle = isle
                break

    @property
    def bots(self):
        return self.isle.bots

    @property
    def cost_matrix(self):
        if self.__cost_matrix is None:
            self.__cost_matrix = get_distance_matrix(self.bots, self.isle.opponent_bots)
            self.__cost_matrix = self.__cost_matrix ** 2
        return self.__cost_matrix

    def affectation_matrix(self):
        row_ind, col_ind = linear_sum_assignment(self.cost_matrix)
        return pd.DataFrame({'bot': np.array([e[-1] for e in self.cost_matrix.index.tolist()])[row_ind],
                             'target': np.array([e[-1] for e in self.cost_matrix.columns.tolist()])[col_ind]})

    def move(self):
        affectation_matrix = self.affectation_matrix()
        only_moves = affectation_matrix[affectation_matrix['bot'] != affectation_matrix['target']]
        for i in only_moves.index:
            bot = only_moves.loc[i]['bot']
            if self.can_move(bot):
                self.player.actions.append(Move(1, bot, only_moves.loc[i]['target']))

    def can_move(self, bot):
        return True

    def spawn(self):
        if (datetime.now() - self.game.step_start).total_seconds() < 0.045:
            try:
                self.player.actions.append(Spawn(1, self.isle.gamer_tiles[0]))
            except:
                pass
        self.player.actions.append(Spawn(1, self.game.gamer.spawn_able_tiles[-1]))
        return

class CleanFormation(BotFormation):
    def __init__(self, player, game, isle):
        super().__init__(player, game)
        self.isle = isle
        self.__cost_matrix = None

    def update(self, player, game):
        super().update(player, game)
        self.__cost_matrix = None
        for isle in self.game.isles:
            if isle.id == self.isle.id:
                self.isle = isle
                break

    @property
    def bots(self):
        return self.isle.bots

    @property
    def cost_matrix(self):
        if self.__cost_matrix is None:
            self.__cost_matrix = get_distance_matrix(self.bots, self.isle.neutral_tiles)
            self.__cost_matrix = self.__cost_matrix ** 2
        return self.__cost_matrix

    def affectation_matrix(self):
        row_ind, col_ind = linear_sum_assignment(self.cost_matrix)
        return pd.DataFrame({'bot': np.array([e[-1] for e in self.cost_matrix.index.tolist()])[row_ind],
                             'target': np.array([e[-1] for e in self.cost_matrix.columns.tolist()])[col_ind]})

    def move(self):
        affectation_matrix = self.affectation_matrix()
        only_moves = affectation_matrix[affectation_matrix['bot'] != affectation_matrix['target']]
        for i in only_moves.index:
            bot = only_moves.loc[i]['bot']
            if self.can_move(bot):
                self.player.actions.append(Move(1, bot, only_moves.loc[i]['target']))
        # neutrals = len(self.isle.neutral_tiles)
        # for bot in self.bots:
        #     if self.can_move(bot):
        #         self.player.actions.append(Move(1, bot, self.isle.neutral_tiles[np.random.randint(neutrals)]))

    def spawn(self):
        if (datetime.now() - self.game.step_start).total_seconds() < 0.045:
            try:
                self.player.actions.append(Spawn(1, self.isle.gamer_tiles[0]))
            except:
                pass
        self.player.actions.append(Spawn(1, self.game.gamer.spawn_able_tiles[-1]))
        return

    def can_move(self, bot):
        return True
