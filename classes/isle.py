from .const import ME, OPP


class Isle:
    def __init__(self, tiles):
        self.tiles = tiles
        self.x_list = []
        self.y_list = []
        self.gamer_tiles = []
        self.gamer_bots = []
        self.opponent_tiles = []
        self.opponent_bots = []
        self.neutral_tiles = []
        for tile in self.tiles:
            self.dispatch_tile(tile)
            self.x_list.append(tile.x)
            self.y_list.append(tile.y)
        self.__owners = None
        self.__bots = None
        self.__bots_dict = {}
        self.__random_tile = None
        self.__width = None
        self.__height = None
        self.x_min = min(self.x_list)
        self.x_max = max(self.x_list)
        self.y_min = min(self.y_list)
        self.y_max = max(self.y_list)
        self.id = f'{len(self.tiles)}_({self.x_min}/{self.x_max} ,{self.y_min}/{self.y_max})'

    def __len__(self):
        return len(self.tiles)

    def dispatch_tile(self, tile):
        if tile.owner == ME:
            self.gamer_tiles.append(tile)
            if tile.units > 0:
                self.gamer_bots.append(tile)
            return
        if tile.owner == OPP:
            self.opponent_tiles.append(tile)
            if tile.units > 0:
                self.opponent_bots.append(tile)
            return
        self.neutral_tiles.append(tile)
        return

    @property
    def owners(self):
        if self.__owners is None:
            self.__owners = ([], [ME])[len(self.gamer_tiles) > 0] + ([], [OPP])[len(self.opponent_tiles) > 0]
        return self.__owners

    @property
    def bots(self):
        if self.__bots is None:
            self.__bots = self.opponent_bots + self.gamer_bots
        return self.__bots

    @property
    def width(self):
        if self.__width is None:
            self.__width = self.x_max - self.x_min + 1
        return self.__width

    @property
    def height(self):
        if self.__height is None:
            self.__height = self.y_max - self.y_min + 1
        return self.__height
