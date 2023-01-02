import pandas as pd

from .player import Gamer, Opponent
from .tile import Tile
from .const import ME, OPP
from .utils import get_tile_from_list
from .logger import LOGGER
from .isle import Isle
import numpy as np


class Game:
    def __init__(self):
        self.width, self.height = self.get_size()
        self.neutral_tiles = []
        self.gamer = Gamer()
        self.opponent = Opponent()
        self.logger = []
        self.step = 0
        self.isles = []
        self.impact_step = self.width // 2 + 1
        self.__grid = None
        self.__neutral_scrap_tiles = None
        self.__neutral_grass_tiles = None

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
        if self.__neutral_scrap_tiles is None:
            self.__neutral_scrap_tiles = [tile for tile in self.neutral_tiles if tile.scrap_amount > 0]
        return self.__neutral_scrap_tiles

    @property
    def neutral_grass_tiles(self):
        if self.__neutral_grass_tiles is None:
            self.__neutral_grass_tiles = [tile for tile in self.neutral_tiles if tile.scrap_amount == 0]
        return self.__neutral_grass_tiles

    @property
    def grid(self):
        if self.__grid is None:
            grid_dict = {}
            for tile in self.tiles:
                if tile.y not in grid_dict:
                    grid_dict[tile.y] = {tile.x: tile}
                    continue
                grid_dict[tile.y][tile.x] = tile
            self.__grid = pd.DataFrame(grid_dict)
            self.__grid.index.rename('x', inplace=True)
            self.__grid.columns.rename('y', inplace=True)
            self.__grid = self.__grid.sort_index()
            self.__grid = self.__grid.sort_index(axis=1)
        return self.__grid

    @staticmethod
    def get_size():
        return [int(i) for i in input().split()]

    @staticmethod
    def get_state():
        return [int(k) for k in input().split()]

    def setup(self):
        self.gamer.setup(self)

    def reset(self):
        self.gamer.reset()
        self.opponent.reset()
        self.neutral_tiles = []
        self.__grid = None

    def play(self):
        self.gamer.actions = []
        self.setup()
        self.gamer.build_policy(self)
        self.gamer.spawn_policy(self)
        self.gamer.move_policy(self)
        sequence = ';'.join(LOGGER + self.gamer.str_actions) if len(self.gamer.actions) > 0 else 'WAIT'
        print(sequence)
        return sequence

    def update(self):
        self.step += 1
        self.reset()
        self.gamer.matter, self.opponent.matter = self.get_size()
        for y in range(self.height):
            for x in range(self.width):
                scrap_amount, owner, units, recycler, can_build, can_spawn, in_range_of_recycler = self.get_state()
                tile = Tile(x, y, scrap_amount, owner, units, recycler == 1, can_build == 1, can_spawn == 1,
                            in_range_of_recycler == 1)
                self.dispatch_tile(tile)
        if self.step == 1:
            self.set_sides()
        self.impact_step = self.find_min_impact_step()
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

    def set_sides(self):
        self.gamer.side = 'left'
        if np.mean([bot.x for bot in self.gamer.bots]) >= self.width / 2:
            self.gamer.side = 'right'
        self.opponent.side = ('left', 'right')[self.gamer.side == 'left']
        return

    def get_tile_without_isle_affectation(self):
        return [tile for tile in self.tiles if tile.isle_id is None and tile.scrap_amount > 0]

    def define_isles(self):
        unaffected_tiles = self.get_tile_without_isle_affectation()
        isle_id = 0
        isles_size = []
        isles = []
        while len(unaffected_tiles) > 0 and isle_id < self.width * self.height // 2:
            tile = unaffected_tiles[0]
            isle_tiles = tile.neighborhood(self, unaffected_tiles, isle_id=isle_id)
            isles_size.append(len(isle_tiles))
            isles.append(Isle(isle_id, isle_tiles))
            isle_id += 1
        LOGGER.append(f'MESSAGE Isles {isle_id}, Size {isles_size}')
        return isles

    def find_min_impact_step(self):
        distance = self.gamer.most_sided_bot.get_distance(self.opponent.most_sided_bot)
        return distance // 2 + 1
