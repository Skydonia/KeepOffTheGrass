import numpy as np
import pandas as pd
from .utils import get_tile_without_isle_affectation_and_scrap_amount


class Tile:
    def __init__(self, x: int, y: int, scrap_amount: int, owner: int, units: int, recycler: bool, can_build: bool,
                 can_spawn: bool, in_range_of_recycler: bool):
        self.x = x
        self.y = y
        self.scrap_amount = scrap_amount
        self.owner = owner
        self.units = units
        self.recycler = recycler
        self.can_build = can_build
        self.can_spawn = can_spawn
        self.in_range_of_recycler = in_range_of_recycler
        self.isle_id = None
        self.relative_position = None
        self.grid = None
        self.center = False

    def __repr__(self):
        return f"x={self.x}, y={self.y}, owner={self.owner}, units={self.units}, scrap={self.scrap_amount}"

    def get_distance(self, other):
        return ((other.x - self.x) ** 2 + (other.y - self.y) ** 2) ** 0.5

    def get_distances(self, tiles):
        return [self.get_distance(tile) for tile in tiles]

    def get_around_tiles(self, game):
        tiles = []
        for att in ['left', 'right', 'upper', 'lower']:
            tile = getattr(self, att)(game)
            if tile is not None:
                tiles.append(tile)
        return tiles

    def get_nearest_tile(self, tiles: list):
        if len(tiles) == 0:
            return None
        distances_tiles = self.get_distances(tiles)
        nearest_index = np.argmin(distances_tiles)
        return tiles[nearest_index]

    def scrap_around(self, game):
        possible_tiles = self.get_around_tiles(game) + [self]
        return sum([tile.scrap_amount for tile in possible_tiles] + [self.scrap_amount])

    def free_scrap(self, game):
        possible_tiles = self.get_around_tiles(game)
        return len([t for t in possible_tiles if t.scrap_amount > self.scrap_amount]) * self.scrap_amount

    def neighborhood(self, game, unaffected_tiles, isle_id=0):
        children = [self]
        unaffected_tiles.remove(self)
        # around_tiles = self.get_around_tiles(game, only=unaffected_tiles)
        around_tiles = self.get_around_tiles(game)
        around_tiles = get_tile_without_isle_affectation_and_scrap_amount(around_tiles)
        for tile in around_tiles:
            if tile in unaffected_tiles:
                tile.isle_id = isle_id
                if tile not in children:
                    children += tile.neighborhood(game, unaffected_tiles, isle_id=isle_id)
        return children

    def synchronize_with_others(self, bots):
        relative_position = {'bot': [], 'x': [], 'y': []}
        for bot in bots:
            if bot == self:
                continue
            relative_position['bot'].append(bot)
            for att in ['x', 'y']:
                relative_position[att].append(getattr(bot, att) - getattr(self, att))
        self.relative_position = pd.DataFrame(relative_position)
        return

    def lower(self, game):
        y = self.y + 1
        if y > game.height - 1:
            return None
        return game.grid.loc[self.x, y]

    def upper(self, game):
        y = self.y - 1
        if y < 0:
            return None
        return game.grid.loc[self.x, y]

    def right(self, game):
        x = self.x + 1
        if x > game.width - 1:
            return None
        return game.grid.loc[x, self.y]

    def left(self, game):
        x = self.x - 1
        if x < 0:
            return None
        return game.grid.loc[x, self.y]
