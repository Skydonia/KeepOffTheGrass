import numpy as np
from .logger import LOGGER
from .utils import get_tile_from_list


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

    def __repr__(self):
        return f"x={self.x}, y={self.y}, owner={self.owner}, unit={self.units}, scrap={self.scrap_amount}"

    @property
    def should_build(self):
        return False

    def get_distance(self, other):
        return abs(other.x - self.x) + abs(other.y - self.y)

    def get_nearest_opponent_unit(self, tiles: list):
        units_tiles = [self.get_distance(tile) for tile in tiles if tile.units > 0]
        if len(units_tiles) == 0:
            return None
        nearest_index = np.argmax(units_tiles)
        return tiles[nearest_index]

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
        possible_tiles = self.get_around_tiles(game)
        return sum([tile.scrap_amount for tile in possible_tiles])

    def in_recyclers_line_columns(self, recyclers, only=None):
        if only is None:
            only = ['x', 'y']
        for recycler in recyclers:
            a = 0
            for attrib in only:
                if getattr(recycler, attrib) == getattr(self, attrib):
                    a += 1
            return a > 0
        return False

    @property
    def spawn_number(self):
        if self.can_spawn:
            return 1
        return 0

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
