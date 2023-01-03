from .const import ME


class Frontier:
    def __init__(self, game, isle):
        self.game = game
        self.isle = isle
        self.starting_column = self.isle.width // 2 - self.player.optimal_move * self.isle.width // 5
        self.tiles = self.game.grid.loc[self.starting_column].tolist()
        self.push()

    @property
    def player(self):
        return self.game.gamer

    def push(self):
        for i, tile in enumerate(self.tiles):
            self.push_frontier_element(i)
        self.tiles = [t for t in self.tiles if t in self.isle.tiles]
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

    def update(self, game, isle):
        self.game = game
        self.isle = isle
        self.tiles = [self.game.grid.loc[tile.x, tile.y] for tile in self.tiles]
        self.push()
