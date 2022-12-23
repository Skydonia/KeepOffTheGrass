import pandas as pd
import numpy as np

from .actions import Move, Spawn, Build
from .logger import LOGGER
from .const import RECYCLER_COST, BOT_COST


class Player:
    def __init__(self, name: str):
        self.name = name
        self.tiles = []
        self.matter = 0
        self.spawned_recyclers = 0

    def __repr__(self):
        return f"{self.name}: {len(self.tiles)}"

    @property
    def bots(self):
        return [tile for tile in self.tiles if tile.units > 0]

    @property
    def recyclers(self):
        return [tile for tile in self.tiles if tile.recycler]

    @property
    def spawn_able_tiles(self):
        return [tile for tile in self.tiles if tile.can_spawn]

    @property
    def build_able_tiles(self):
        return [tile for tile in self.tiles if tile.can_build]

    @property
    def buildable_bots(self):
        return self.matter // BOT_COST

    @property
    def buildable_recyclers(self):
        return self.matter // RECYCLER_COST

    def get_enemy_distances(self, enemy):
        distances = []
        for enemy_bot in enemy.bots:
            nearest_bot = enemy_bot.get_nearest_tile(self.bots)
            if nearest_bot is not None:
                distance = enemy_bot.get_distance(nearest_bot)
                distances.append({'bot': nearest_bot, 'target': enemy_bot, 'distance': distance})
        if len(distances) == 0:
            return distances
        distances = pd.DataFrame(distances).sort_values('distance')
        return distances

    def get_tile_distances(self, enemy):
        distances = []
        for tile in enemy.tiles:
            nearest_tile = tile.get_nearest_tile(self.tiles)
            if nearest_tile is not None:
                distance = tile.get_distance(nearest_tile)
                distances.append({'tile': nearest_tile, 'distance': distance})
        if len(distances) == 0:
            return
        distances = pd.DataFrame(distances).sort_values('distance')
        return distances

    def get_closest_tile_to_enemy(self, enemy):
        distances = self.get_tile_distances(enemy)
        if len(distances) == 0:
            return None
        return distances.iloc[0]['tile']

    def get_recycling_scrap_infos(self, game):
        scraps = []
        for tile in self.build_able_tiles:
            scrap = tile.scrap_around(game)
            scraps.append({'tile': tile, 'scrap': scrap})
        distances = pd.DataFrame(scraps).sort_values('scrap', ascending=False)
        return distances


class Opponent(Player):
    def __init__(self):
        super().__init__(name='Opponent')


class Gamer(Player):
    def __init__(self):
        super().__init__(name='Gamer')
        self.actions = []

    @property
    def str_actions(self):
        return [str(action) for action in self.actions]

    def spawn_defenders(self, enemy):
        distances = self.get_enemy_distances(enemy)
        if len(distances) == 0:
            return
        danger = distances[distances['distance'] < 2].sort_values('distance')
        for i in danger.index:
            amount = danger.loc[i]['target'].units
            self.actions.append(Spawn(amount, danger.loc[i]['bot']))
        return

    def get_possible_move_tiles(self, game):
        _tiles = game.neutral_scrap_tiles + game.opponent.tiles
        tiles = []
        for tile in _tiles:
            if tile not in game.opponent.recyclers:
                if len(game.opponent.recyclers) == 0:
                    tiles.append(tile)
                    continue
                if min(tile.get_distances(game.opponent.recyclers)) > 1:
                    tiles.append(tile)
        return tiles

    def spread_bot(self, enemy):
        distances = self.get_tile_distances(enemy)
        for b in range(self.buildable_bots):
            self.actions.append(Spawn(1, distances.iloc[b]['tile']))
        return

    def check_bots_recyclers_ratio(self, n):
        nb_recyclers = len(self.recyclers)
        if nb_recyclers == 0:
            return True
        return (len(self.bots) / nb_recyclers) >= n

    def spawn_function(self, enemy):
        self.spawn_defenders(enemy)
        # closest_tile = self.get_closest_tile_to_enemy(enemy)
        # if closest_tile is not None:
        #     amount = closest_tile.spawn_number
        #     if amount > 0:
        #         self.actions.append(Spawn(amount, closest_tile))
        self.spread_bot(enemy)
        return

    def build_function(self, game):
        max_recyclers = game.width
        max_recycler_per_step = 1
        if self.spawned_recyclers < max_recyclers and game.step > 1 and self.check_bots_recyclers_ratio(4):
            self.spawned_recyclers += 1
            scraps = self.get_recycling_scrap_infos(game)
            scraps['right'] = scraps['tile'].apply(lambda x: game.frontier - x.x)
            scraps['left'] = scraps['tile'].apply(lambda x: x.x - game.frontier)
            scraps = scraps.sort_values(game.side, ascending=False)
            for i in range(min(self.buildable_recyclers, max_recycler_per_step)):
                tile = scraps.iloc[i]['tile']
                if not tile.in_recyclers_line_columns(self.recyclers, only=['y']):
                    self.actions.append(Build(tile))
        return

    def move_function(self, game):
        max_stacked = 1
        for bot in self.bots:
            if bot.units > max_stacked:
                for _ in range(max_stacked + 1, bot.units):
                    random_tile = bot.chose_random_near_tile(game)
                    self.actions.append(Move(1, bot, random_tile))
            target_tile = bot.get_nearest_tile(self.get_possible_move_tiles(game))
            self.actions.append(Move(min(bot.units, 2), bot, target_tile))
        return

    def play(self, game):
        self.actions = []
        self.build_function(game)
        self.spawn_function(game.opponent)
        self.move_function(game)
        sequence = ';'.join(LOGGER + self.str_actions) if len(self.actions) > 0 else 'WAIT'
        print(sequence)
        return sequence
