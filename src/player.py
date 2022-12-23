from .actions import Move, Spawn, Build


class Player:
    def __init__(self, name: str):
        self.name = name
        self.tiles = []

    def __repr__(self):
        return f"{self.name}: {len(self.tiles)}"

    @property
    def units(self):
        return [tile for tile in self.tiles if tile.units > 0]

    @property
    def recyclers(self):
        return [tile for tile in self.tiles if tile.recycler]

    @property
    def spawn_able_tiles(self):
        return [tile for tile in self.tiles if tile.can_spawn]

    @property
    def build_able_tiles(self):
        return [tile for tile in self.tiles if tile.can_build]


class Opponent(Player):
    def __init__(self):
        super().__init__(name='Opponent')


class Gamer(Player):
    def __init__(self):
        super().__init__(name='Gamer')
        self.actions = []

    @property
    def str_actions(self):
        return [str(action) for action in self.actions]

    def spawn_function(self):
        for tile in self.spawn_able_tiles:
            amount = tile.spawn_number
            if amount > 0:
                self.actions.append(Spawn(amount, tile))
        return

    def build_function(self):
        for tile in self.build_able_tiles:
            if tile.should_build:
                self.actions.append(Build(tile))
        return

    def move_function(self, game):
        for tile in self.units:
            # self.actions.append(Move(tile.units, tile, tile.get_nearest_opponent_unit(game.opponent.units)))
            self.actions.append(Move(tile.units, tile, tile.get_nearest_empty(game.neutral_tiles + game.opponent.tiles)))
        return

    def play(self, game):
        self.build_function()
        self.spawn_function()
        self.move_function(game)
        sequence = ';'.join(self.str_actions) if len(self.actions) > 0 else 'WAIT'
        print(sequence)
        return sequence
