import copy

from .const import ME
import operator

class Frontier:
    def __init__(self, game, isle):
        self.game = game
        self.isle = isle
        # self.distance_grid = self.get_center_distance_grid(max_radius=self.game.impact)

        # self.center = self.find_center()
        # self.opp_center = self.find_opp_center()
        # self.distance = self.center.get_distance(self.opp_center)
        # self.tiles = self.find_beginning_tiles()

        # if self.isle.main:
        #     self.tiles = self.get_tiles_from_radius(3)
        # else:
        #     self.starting_column = self.isle.width // 2 - self.player.optimal_move * self.isle.width // 5
        #     self.tiles = self.game.grid.loc[self.starting_column].tolist()

        self.tiles = self.get_tiles_from_radius(self.game.impact)
        self.push()

    @property
    def player(self):
        return self.game.gamer

    # def find_center(self):
    #     for tile in self.isle.gamer_tiles:
    #         if tile not in self.isle.gamer_bots:
    #             return tile
    #     return self.player.most_sided_bot
    #
    # def find_opp_center(self):
    #     for tile in self.isle.opponent_tiles:
    #         if tile not in self.isle.opponent_tiles:
    #             return tile
    #     return self.game.opponent.most_sided_bot
    #
    # def find_beginning_tiles(self):
    #     rayon = self.distance // 2
    #     tiles = []
    #     for y in range(self.isle.width):
    #         delta_y = abs(y - self.center.y)
    #         if delta_y <= rayon:
    #             try:
    #                 delta_x = int((rayon ** 2 - delta_y ** 2) ** 0.5)
    #                 x = delta_x + self.center.x
    #                 if 0 <= x <= self.isle.x_max:
    #                     tiles.append(self.game.grid.loc[x, y])
    #             except:
    #                 continue
    #     return copy.copy(tiles)

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

    def get_tiles_from_radius(self, radius):
        tiles = []
        for y in self.game.center_distance_grid.columns:
            best = None
            best_r = 0
            for x in self.game.center_distance_grid.index.tolist()[::self.player.optimal_move]:
                ops = (operator.le, operator.ge)[self.player.side == 'left']
                if ops(x, self.player.center.x):
                    r = self.game.center_distance_grid.loc[x, y]
                    if r <= radius ** 2:
                        if best is None:
                            best = self.game.grid.loc[x, y]
                            best_r = r
                        if r > best_r:
                            best = self.game.grid.loc[x, y]
                            best_r = r
                        # tiles.append(self.game.grid.loc[x, y])
                        # break
            if best is not None:
                tiles.append(best)
        return tiles

