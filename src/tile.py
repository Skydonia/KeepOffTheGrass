import numpy as np
import pandas as pd

from .logger import LOGGER
from .utils import get_tile_from_list, count_bots_in_grid


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

    def __repr__(self):
        return f"x={self.x}, y={self.y}, owner={self.owner}, units={self.units}, scrap={self.scrap_amount}"

    @property
    def should_build(self):
        return False

    def get_distance(self, other):
        return abs(other.x - self.x) + abs(other.y - self.y)

    def get_distances(self, tiles):
        return [self.get_distance(tile) for tile in tiles]

    def get_nearest_tile(self, tiles: list):
        if len(tiles) == 0:
            return None
        distances_tiles = self.get_distances(tiles)
        nearest_index = np.argmin(distances_tiles)
        return tiles[nearest_index]

    def chose_random_near_tile(self, game):
        possible_tiles = self.get_around_tiles(game)
        index = np.random.randint(len(possible_tiles))
        return possible_tiles[index]

    def scrap_around(self, game):
        possible_tiles = self.get_around_tiles(game) + [self]
        return sum([tile.scrap_amount for tile in possible_tiles] + [self.scrap_amount])

    def get_around_tiles(self, game, tiles=None):
        if tiles is None:
            tiles = game.tiles
        possible_tiles = []
        for x in [self.x - 1, self.x + 1]:
            if 0 <= x < game.width:
                new_tile = get_tile_from_list(x, self.y, tiles)
                if new_tile is not None:
                    possible_tiles.append(new_tile)
        for y in [self.y - 1, self.y + 1]:
            if 0 <= y < game.height:
                new_tile = get_tile_from_list(self.x, y, tiles)
                if new_tile is not None:
                    possible_tiles.append(new_tile)
        return possible_tiles

    def neighborhood(self, game, unaffected_tiles, isle_id=0):
        children = [self]
        unaffected_tiles.remove(self)
        around_tiles = self.get_around_tiles(game, tiles=unaffected_tiles)
        for tile in around_tiles:
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
                relative_position[att].append(getattr(bot,att) - getattr(self,att))
        self.relative_position = pd.DataFrame(relative_position)
        return

    @property
    def lower_bots(self):
        return self.relative_position[self.relative_position['y'] < 0].index.tolist()

    @property
    def upper_bots(self):
        return self.relative_position[self.relative_position['y'] > 0].index.tolist()
