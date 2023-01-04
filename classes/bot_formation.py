import pandas as pd
from .logger import LOGGER
from scipy.optimize import linear_sum_assignment
import numpy as np
from .utils import get_distance_matrix, get_recycling_scrap_infos, get_tile_distances
from .const import ME, OPP, BOT_COST
from .frontier import Frontier
from .actions import Move, Spawn, Build
from datetime import datetime


class BotFormation:
    def __init__(self, player, game, isle):
        self.name = self.__class__.__name__
        self.player = player
        self.game = game
        self.isle = isle

    @property
    def grid(self):
        return self.game.grid

    @property
    def x_max(self):
        return self.isle.x_max

    @property
    def y_max(self):
        return self.isle.y_max

    @property
    def tiles(self):
        return self.isle.tiles

    @property
    def bots(self):
        return self.isle.gamer_bots

    @property
    def unit_bots(self):
        return [bot for bot in self.bots for _ in range(bot.units)]

    def move(self):
        return

    def default_build(self):
        # if self.game.step == 2:
        if 2 <= self.game.step <= max(2, self.game.impact // 1.8):
            scrap_table = get_recycling_scrap_infos([tile for tile in self.isle.gamer_tiles if tile.units == 0],
                                                    self.game)
            self.player.actions.append(Build(scrap_table.iloc[0]['tile']))
        distances = get_tile_distances(self.player.build_able_tiles, self.isle.opponent_bots)
        if distances is None:
            return
        self.avoid_inf_loop()
        d = distances[distances['distance'] <= 1]
        for i in d.index:
            tile = d.loc[i]['tile']
            sided = getattr(tile, ('left', 'right')[self.player.side == 'left'])(self.game)
            if sided == d.loc[i]['target']:
                self.player.actions.append(Build(tile))
        return

    def avoid_inf_loop(self):
        if len(self.bots) > 0:
            i = np.argmax([bot.units for bot in self.bots])
            if self.bots[i].units > 20:
                ptn = self.bots[i]
                self.player.actions.append(Build(self.game.grid.loc[ptn.x - self.player.optimal_move, ptn.y]))
        return

    def build(self):
        self.default_build()

    def bot_spawner(self, distances, bots: int = None):
        if len(distances) == 0:
            return
        if bots is None:
            bots = self.player.buildable_bots
        bot_to_spawn = min(bots, self.player.buildable_bots)
        b = 0
        while (bot_to_spawn > 0) and (b < len(distances)):
            stack = distances.iloc[b]['unit_gap']
            if stack < 0:
                stack = 0
            if bot_to_spawn >= stack > 0:
                self.player.actions.append(Spawn(stack, distances.iloc[b]['tile']))
                bot_to_spawn -= stack
            b += 1
        return

    def backup_spawn(self, limit=30):
        op_distance = get_tile_distances(self.isle.gamer_tiles, self.isle.opponent_tiles)
        op_distance['unit_gap'] = 1
        self.bot_spawner(op_distance, bots=(self.player.matter - limit) // BOT_COST)
        return

    def defend_spawn(self, bots: int = None):
        distances = get_tile_distances(self.bots, self.isle.opponent_bots)
        distances = distances.sort_values('unit_gap')
        distances = distances[distances['unit_gap'] <= self.player.buildable_bots]
        self.bot_spawner(distances, bots)

    def spawn(self):
        distances = get_tile_distances(self.tiles, self.isle.opponent_bots)
        if distances is None:
            self.backup_spawn(limit=0)
            return
        contact = distances[distances['distance'] <= 1]
        self.bot_spawner(contact)
        # if len(self.bots) > 0:
        #     self.defend_spawn()
        # if self.player.matter > 30:
        self.backup_spawn(limit=0)

    def move_forward(self, bot):
        x = max(bot.x + self.player.optimal_move, 0)
        if self.player.side == 'left':
            x = min(bot.x + self.player.optimal_move, self.x_max)
        # y = bot.y - 1
        # if abs(self.isle.y_max - y) > bot.y:
        #     y = bot.y + 1
        # target = self.grid.loc[x, y]
        # if target.scrap_amount == 0:
        target = self.grid.loc[x, bot.y]
        self.player.actions.append(Move(bot.units,
                                        bot,
                                        target
                                        ))
        return

    def update(self, player, game, isle):
        self.player = player
        self.game = game
        self.isle = isle


class ConquerFormation(BotFormation):
    def __init__(self, player, game, isle):
        super().__init__(player, game, isle)
        self.frontier = Frontier(self.game, self.isle)
        self.__cost_matrix = None

    def update(self, player, game, isle):
        super().update(player, game, isle)
        self.__cost_matrix = None
        self.frontier.update(self.game, self.isle)

    @property
    def cost_matrix(self):
        if self.__cost_matrix is None:
            self.__cost_matrix = get_distance_matrix(self.unit_bots, self.frontier.tiles)
            # opponent_distance = get_distance_matrix([self.game.opponent.center], self.frontier.tiles)
            # for i in self.__cost_matrix.index:
            #     self.__cost_matrix.loc[i] += opponent_distance.iloc[0]
            # self.__cost_matrix = self.__cost_matrix ** 2
            # if len(self.__cost_matrix) > 0:
            #     self.__cost_matrix[self.__cost_matrix.columns[0]] -= 2
            #     self.__cost_matrix[self.__cost_matrix.columns[-1]] -= 2
        return self.__cost_matrix

    def affectation_matrix(self):
        row_ind, col_ind = linear_sum_assignment(self.cost_matrix)
        return pd.DataFrame({'bot': np.array([e[-1] for e in self.cost_matrix.index.tolist()])[row_ind],
                             'target': np.array([e[-1] for e in self.cost_matrix.columns.tolist()])[col_ind]})

    def move(self):
        # locked_dict = {}
        affectation_matrix = self.affectation_matrix()
        only_moves = affectation_matrix[affectation_matrix['bot'] != affectation_matrix['target']]
        LOGGER.append(f'MESSAGE Frontier {[t.x for t in self.frontier.tiles]}')
        for i in only_moves.index:
            bot = only_moves.loc[i]['bot']
            locked = self.get_locked_units(bot)
            if self.can_move(locked):
                self.player.actions.append(Move(1, bot, only_moves.loc[i]['target']))
            #     continue
            # if bot.units > locked:
            #     if (bot.x, bot.y) not in locked_dict:
            #         locked_dict[(bot.x, bot.y)] = locked
            #     if bot.units > locked_dict[(bot.x, bot.y)]:
            #         self.player.actions.append(Move(1, bot, only_moves.loc[i]['target']))
            #         locked_dict[(bot.x, bot.y)] += 1
        for bot in self.bots:
            locked = self.get_locked_units(bot)
            if self.can_move(locked):
                self.move_forward(bot)

    @staticmethod
    def can_move(locked):
        if locked > 0:
            return False
        return True

    def get_locked_units(self, bot):
        backup = getattr(bot, self.player.side)(self.game)
        sided = getattr(bot, ('left', 'right')[self.player.side == 'left'])(self.game)
        upper = getattr(bot, 'upper')(self.game)
        lower = getattr(bot, 'lower')(self.game)
        total_locked = 0
        for other in [sided, upper, lower]:
            if other is not None:
                if other.owner == OPP:
                    total_locked += other.units
        if backup is not None:
            if backup.owner == ME:
                total_locked -= backup.units
        return total_locked

    # def backup_spawn(self, limit=30):
    #     n_bots = (self.player.matter - limit) // BOT_COST
    #     op_distance = get_distance_matrix(self.isle.gamer_tiles,
    #                                       [self.game.opponent.center for _ in range(n_bots)]) ** 2
    #     row_ind, col_ind = linear_sum_assignment(op_distance)
    #     # bots = np.array([e[-1] for e in op_distance.columns.tolist()])[col_ind]
    #     bots = np.array([e[-1] for e in op_distance.index.tolist()])[row_ind]
    #     for bot in bots:
    #         self.player.actions.append(Spawn(1, bot))
    #     return


class CombatFormation(BotFormation):
    def __init__(self, player, game, isle):
        super().__init__(player, game, isle)
        self.__cost_matrix = None

    def update(self, player, game, isle):
        super().update(player, game, isle)
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
            self.player.actions.append(Move(1, bot, only_moves.loc[i]['target']))
        for bot in self.bots:
            self.move_forward(bot)

    def spawn(self):
        if len(self.isle.gamer_bots) > 0:
            self.player.actions.append(Spawn(self.player.buildable_bots, self.isle.gamer_bots[0]))
        return


class CleanFormation(BotFormation):
    def __init__(self, player, game, isle):
        super().__init__(player, game, isle)
        self.__cost_matrix = None

    def update(self, player, game, isle):
        super().update(player, game, isle)
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
            self.player.actions.append(Move(1, bot, only_moves.loc[i]['target']))

    def spawn(self):
        isles = [i.id for i in self.player.isles]
        for formation in self.player.strategy.formations:
            f = self.player.strategy.formations[formation]
            if type(f) == CombatFormation:
                isle = f.isle
                if ME not in isle.owners or isle.id not in isles:
                    del f
                    continue
                return
        self.player.actions.append(Spawn(1, self.isle.gamer_tiles[0]))
        return
