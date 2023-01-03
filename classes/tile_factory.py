from .utils import Singleton
from .tile import Tile


class TileFactory(metaclass=Singleton):
    def __init__(self):
        self.n_tiles = 0
        self.step = 0
        self.tiles = {}

    def create_tile(self, game, x: int, y: int, scrap_amount: int, owner: int, units: int, recycler: bool,
                    can_build: bool, can_spawn: bool, in_range_of_recycler: bool):
        self.n_tiles += 1
        tile = Tile(x, y, scrap_amount, owner, units, recycler == 1, can_build == 1, can_spawn == 1,
                    in_range_of_recycler == 1)
        game.dispatch_tile(tile)
