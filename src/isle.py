class Isle:
    def __init__(self, isle_id, tiles):
        self.id = isle_id
        self.tiles = tiles
        self.__owners = []

    def __len__(self):
        return len(self.tiles)

    def owners(self):
        if len(self.__owners) > 1:
            self.__owners = list(set([tile.owner for tile in self.tiles]))
        return self.__owners
