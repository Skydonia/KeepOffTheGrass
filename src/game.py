from .player import Gamer, Opponent
from .tile import Tile
from .const import ME, OPP


class Game:
    def __init__(self):
        self.width, self.height = self.get_size()
        self.neutral_tiles = []
        self.gamer = Gamer()
        self.opponent = Opponent()
        self.logger = []
        self.step = 0

    def __getitem__(self, x):
        if type(x) == list:
            items = []
            for ref in x:
                for tile in self.tiles:
                    if (tile.x, tile.y) == (ref[0], ref[-1]):
                        items.append(tile)
            return items
        for tile in self.tiles:
            if (tile.x, tile.y) == (x[0], x[-1]):
                return tile
        return None

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

    @staticmethod
    def get_size():
        return [int(i) for i in input().split()]

    @staticmethod
    def get_state():
        return [int(k) for k in input().split()]

    def update(self):
        self.step += 1
        self.gamer.matter, self.opponent.matter = self.get_state()
        self.gamer.tiles = []
        self.opponent.tiles = []
        self.neutral_tiles = []
        for y in range(self.height):
            for x in range(self.width):
                scrap_amount, owner, units, recycler, can_build, can_spawn, in_range_of_recycler = self.get_state()
                tile = Tile(x, y, scrap_amount, owner, units, recycler == 1, can_build == 1, can_spawn == 1,
                            in_range_of_recycler == 1)
                self.dispatch_tile(tile)

    def dispatch_tile(self, tile: Tile):
        if tile.owner == ME:
            self.gamer.tiles.append(tile)
            return
        if tile.owner == OPP:
            self.opponent.tiles.append(tile)
            return
        self.neutral_tiles.append(tile)
        return
