import numpy as np
from .logger import LOGGER


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

    def get_nearest_tile(self, tiles: list):
        if len(tiles) == 0:
            return None
        distances_tiles = self.get_distances(tiles)
        nearest_index = np.argmin(distances_tiles)
        return tiles[nearest_index]

    def chose_random_near_tile(self, game):
        possible_tiles = []
        for x in [self.x, self.x+1]:
            for y in [self.y, self.y + 1]:
                if x < game.width and y < game.height:
                    possible_tiles.append(game[x, y])
        index = np.random.randint(len(possible_tiles))
        return possible_tiles[index]


    @property
    def spawn_number(self):
        if self.can_spawn:
            return 1
        return 0
