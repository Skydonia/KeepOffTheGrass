from .const import ME, OPP
import copy


class Frontier:
    def __init__(self, game):
        self.game = game
        self.starting_column = copy.deepcopy(self.player.most_sided_bot.x) + self.player.optimal_move
        self.tiles = self.game.grid.loc[self.starting_column].tolist()
        self.secured = False

    @property
    def player(self):
        return self.game.gamer

    def push(self):
        for tile in self.tiles:
            sided = self.game.grid.loc[tile.x + self.player.optimal_move, tile.y]
            while (tile.scrap_amount == 0 or
                   tile.recycler or
                   sided.scrap_amount == 0 or
                   (tile.units > 0 and tile.owner == ME)) and (
                    0 < sided.x < self.game.width - 1):
                tile = sided
                sided = self.game.grid.loc[tile.x + self.player.optimal_move, tile.y]
        return

    def is_secured(self):
        for tile in self.tiles:
            if tile.owner != ME and tile.scrap_amount > 0:
                return False
        return True

    def update(self, game):
        self.game = game
