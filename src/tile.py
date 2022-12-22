import numpy as np


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
    def spawn_number(self):
        return 0

    @property
    def should_build(self):
        return False

    def get_distance(self, other):
        return (other.x - self.x) ** 2 + (other.y - self.y) ** 2

    def get_nearest_opponent(self, tiles: list):
        units_tiles = [self.get_distance(tile) for tile in tiles if tile.units > 0]
        if len(units_tiles) == 0:
            return None
        nearest_index = np.argmax(units_tiles)
        return tiles[nearest_index]