from .const import ME, OPP
import copy
from .logger import LOGGER


class Frontier:
    def __init__(self, game):
        self.game = game
        self.starting_column = copy.deepcopy(self.player.most_sided_bot.x)  # + self.player.optimal_move
        self.tiles = self.game.grid.loc[self.starting_column].tolist()
        self.secured = False

    @property
    def player(self):
        return self.game.gamer

    def push(self):
        for i, tile in enumerate(self.tiles):
            self.push_frontier_element(i)
        return

    def push_frontier_element(self, i):
        tile = self.tiles[i]
        sided = self.game.grid.loc[tile.x + self.player.optimal_move, tile.y]
        while (
                tile.scrap_amount == 0 or
                tile.recycler or
                sided.scrap_amount == 0 or
                sided.recycler or
                tile.owner == ME or
                sided.owner == ME
        ) and (
                0 < sided.x < self.game.width - 1):
            tile = sided
            sided = self.game.grid.loc[sided.x + self.player.optimal_move, sided.y]
        self.tiles[i] = tile

    def is_secured(self):
        for tile in self.tiles:
            if tile.owner != ME and tile.scrap_amount > 0:
                return False
        return True

    def update(self, game):
        self.game = game
        self.tiles = [self.game.grid.loc[tile.x, tile.y] for tile in self.tiles]
