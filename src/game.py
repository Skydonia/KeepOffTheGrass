from .player import Gamer, Opponent
from .tile import Tile
from .const import ME, OPP
from .utils import get_tile_from_list
from .logger import LOGGER
import numpy as np


class Game:
    def __init__(self):
        self.width, self.height = self.get_size()
        self.neutral_tiles = []
        self.gamer = Gamer()
        self.opponent = Opponent()
        self.logger = []
        self.step = 0
        self.side = None
        self.isles = 1

    def __getitem__(self, x):
        return get_tile_from_list(x[0], x[-1], self.tiles)

    @property
    def size(self):
        return self.width * self.height

    @property
    def players(self):
        return [self.gamer, self.opponent]

    @property
    def tiles(self):
        return self.neutral_tiles + self.gamer.tiles + self.opponent.tiles

    @property
    def neutral_scrap_tiles(self):
        return [tile for tile in self.neutral_tiles if tile.scrap_amount > 0]

    @property
    def neutral_grass_tiles(self):
        return [tile for tile in self.neutral_tiles if tile.scrap_amount == 0]

    @property
    def frontier(self):
        return (self.width // 2 + 1, self.width // 2 + 1)[self.width % 2 == 0]

    @staticmethod
    def get_size():
        return [int(i) for i in input().split()]

    @staticmethod
    def get_state():
        return [int(k) for k in input().split()]

    def update(self):
        self.step += 1
        self.gamer.matter, self.opponent.matter = self.get_size()
        self.gamer.tiles = []
        self.opponent.tiles = []
        self.neutral_tiles = []
        for y in range(self.height):
            for x in range(self.width):
                scrap_amount, owner, units, recycler, can_build, can_spawn, in_range_of_recycler = self.get_state()
                tile = Tile(x, y, scrap_amount, owner, units, recycler == 1, can_build == 1, can_spawn == 1,
                            in_range_of_recycler == 1)
                self.dispatch_tile(tile)
        if self.step == 1:
            self.set_side()
        self.isles = self.define_isles()

    def dispatch_tile(self, tile: Tile):
        if tile.owner == ME:
            self.gamer.tiles.append(tile)
            return
        if tile.owner == OPP:
            self.opponent.tiles.append(tile)
            return
        self.neutral_tiles.append(tile)
        return

    def set_side(self):
        if np.mean([bot.x for bot in self.gamer.bots]) >= self.width / 2:
            self.side = 'right'
            return
        self.side = 'left'

    def get_tile_without_isle_affectation(self):
        return [tile for tile in self.tiles if tile.isle_id is None and tile.scrap_amount > 0]

    def define_isles(self):
        unaffected_tiles = self.get_tile_without_isle_affectation()
        isle_id = 0
        isles_size = []
        while len(unaffected_tiles) > 0 and isle_id < 100:
            tile = unaffected_tiles[0]
            isle_tiles = tile.neighborhood(self, unaffected_tiles, isle_id=isle_id)
            isles_size.append(len(isle_tiles))
            isle_id += 1
        LOGGER.append(f'MESSAGE Isles {isle_id}, Size {isles_size}')
        return isle_id
