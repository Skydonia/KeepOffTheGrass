from .const import ME, OPP, NONE


class Isle:
    def __init__(self, tiles):
        self.tiles = tiles
        self.gamer_tiles = []
        self.gamer_bots = []
        self.opponent_tiles = []
        self.opponent_bots = []
        self.neutral_tiles = []
        for tile in self.tiles:
            self.dispatch_tile(tile)
        self.__owners = None
        self.__bots = None
        self.__bots_dict = {}
        self.__random_tile = None
        self.id = f'{len(self.tiles)}_{self.owners}'

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
    def prioritize(self):
        if len(self.bots) == 0 and ME in self.owners:
            return True
        return False
