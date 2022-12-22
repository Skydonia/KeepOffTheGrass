from .player import Gamer, Opponent
from .tile import Tile
from .const import ME, OPP


class Game:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.neutral_tiles = []
        self.gamer = Gamer()
        self.opponent = Opponent()

    def __getitem__(self, x, y=None):
        if y is None:
            items = []
            for _x, _y in x:
                for tile in self.tiles:
                    if (tile.x, tile.y) == (_x, _y):
                        items.append(tile)
            return items
        for tile in self.tiles:
            if (tile.x, tile.y) == (x, y):
                return tile
        return None

    @property
    def players(self):
        return [self.gamer, self.opponent]

    @property
    def tiles(self):
        return self.neutral_tiles + self.gamer.tiles + self.opponent.tiles

    def update(self):
        for y in range(self.height):
            for x in range(self.width):
                scrap_amount, owner, units, recycler, can_build, can_spawn, in_range_of_recycler = [int(k) for k in
                                                                                                    input().split()]
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
