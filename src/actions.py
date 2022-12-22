class Action:
    def __init__(self):
        self.name = self.__class__.__name__.upper()

    def __str__(self):
        return "WAIT"


class Spawn(Action):
    def __init__(self, tile, amount: int):
        super().__init__()
        self.tile = tile
        self.amount = amount

    def __str__(self):
        return f'{self.name} {self.amount} {self.tile.x} {self.tile.y}'


class Build(Action):
    def __init__(self, tile):
        super().__init__()
        self.tile = tile

    def __str__(self):
        return f'{self.name} {self.tile.x} {self.tile.y}'


class Move(Action):
    def __init__(self, amount, from_tile, target_tile):
        super().__init__()
        self.amount = amount
        self.from_tile = from_tile
        self.target_tile = target_tile

    def __str__(self):
        return f'{self.name} {self.from_tile.x} {self.from_tile.y} {self.target_tile.x} {self.target_tile.y}'
