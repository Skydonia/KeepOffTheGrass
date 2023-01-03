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
        if self.game.step == 2:
            scrap_table = get_recycling_scrap_infos([tile for tile in self.isle.gamer_tiles if tile.units == 0],
                                                    self.game)
            self.player.actions.append(Build(scrap_table.iloc[0]['tile']))
        distances = get_tile_distances(self.player.build_able_tiles, self.isle.opponent_bots)
        if distances is None:
            return
        d = distances[distances['distance'] <= 1]
        for tile in d['tile'].tolist():
            self.player.actions.append(Build(tile))
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
            return
        contact = distances[distances['distance'] <= 1]
        self.bot_spawner(contact)
        if len(self.bots) > 0:
            self.defend_spawn()
        if self.player.matter > 30:
            self.backup_spawn(limit=0)

    def move_forward(self, bot):
        x = max(bot.x + self.player.optimal_move, 0)
        if self.player.side == 'left':
            x = min(bot.x + self.player.optimal_move, self.x_max)
        self.player.actions.append(Move(bot.units,
                                        bot,
                                        self.grid.loc[x, bot.y]
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
            if self.can_move(bot):
                self.move_forward(bot)

    def can_move(self, bot):
        x = max(bot.x + self.player.optimal_move, 0)
        _x = min(bot.x - self.player.optimal_move, self.x_max)
        if self.player.side == 'left':
            x = min(bot.x + self.player.optimal_move, self.x_max)
            _x = max(bot.x - self.player.optimal_move, 0)
        # backup = getattr(bot, self.player.side)
        # sided = getattr(bot, ('left', 'right')[self.player.side == 'left'])
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
