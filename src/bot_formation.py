import pandas as pd
from .actions import Move
from .logger import LOGGER


class BotFormation:
    def __init__(self, player, game):
        self.player = player
        self.tiles = game.tiles
        self.x_max = game.width
        self.y_max = game.height
        self.__grid = None

    @property
    def bots(self):
        return self.player.bots

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

    def move(self):
        return


class ConquerFormation(BotFormation):

    def move(self):
        for bot in self.bots:
            # if len(bot.relative_position[bot.relative_position['y'] == 0]) > 1:
            #     nb_upper_bot = len(bot.relative_position[bot.relative_position['y'] > 0])
            #     lack_upper = nb_upper_bot - self.y_max - bot.y
            #     nb_lower_bot = len(bot.relative_position[bot.relative_position['y'] < 0])
            #     lack_lower = nb_lower_bot - bot.y
            #     if lack_lower > lack_upper:
            #         self.player.actions.append(Move(1, bot, self.grid.loc[bot.x, bot.y - 1]))
            #         continue
            #     self.player.actions.append(Move(1, bot, self.grid.loc[bot.x, bot.y + 1]))
            #     continue
            LOGGER.append(f'MESSAGE {len(self.grid.index)}, {len(self.grid.columns)}')
            # self.player.actions.append(Move(1, bot, self.grid.loc[bot.x + self.player.optimal_move, bot.y]))
