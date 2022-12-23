import numpy as np
from .const import NONE


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

    def get_nearest_empty_tile(self, tiles: list):
        _tiles = [tile for tile in tiles if (tile.owner == NONE) and (tile.scrap_amount >= 0)]
        distances_tiles = self.get_distances(_tiles)
        if len(distances_tiles) == 0:
            return None
        nearest_index = np.argmin(distances_tiles)
        return _tiles[nearest_index]

    @property
    def spawn_number(self):
        if self.can_spawn:
            return 1
        return 0
