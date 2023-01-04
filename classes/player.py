from .utils import get_most_sided_tile_from_list
from .const import RECYCLER_COST, BOT_COST, ME
from .strategy import Strategy
from .logger import LOGGER


class Player:
    def __init__(self, name: str):
        self.name = name
        self.tiles = []
        self.matter = 0
        self.spawned_recyclers = 0
        self.side = None
        self.center = None
        self.__bots = None
        self.__recyclers = None
        self.__spawn_able_tiles = None
        self.__build_able_tiles = None
        self.__most_sided_bot = None

    def __repr__(self):
        return f"{self.name}: {len(self.tiles)}"

    @property
    def bots(self):
        if self.__bots is None:
            self.__bots = [tile for tile in self.tiles if tile.units > 0]
        return self.__bots

    @property
    def recyclers(self):
        if self.__recyclers is None:
            self.__recyclers = [tile for tile in self.tiles if tile.recycler]
        return self.__recyclers

    @property
    def spawn_able_tiles(self):
        if self.__spawn_able_tiles is None:
            self.__spawn_able_tiles = [tile for tile in self.tiles if tile.can_spawn]
        return self.__spawn_able_tiles

    @property
    def build_able_tiles(self):
        if self.__build_able_tiles is None:
            self.__build_able_tiles = [tile for tile in self.tiles if tile.can_build]
        return self.__build_able_tiles

    @property
    def buildable_bots(self):
        return self.matter // BOT_COST

    @property
    def buildable_recyclers(self):
        return self.matter // RECYCLER_COST

    @property
    def most_sided_bot(self):
        if self.__most_sided_bot is None:
            self.__most_sided_bot = get_most_sided_tile_from_list(self.side, self.bots)
        return self.__most_sided_bot

    def reset(self):
        self.tiles = []
        self.matter = 0
        self.spawned_recyclers = 0
        self.__bots = None
        self.__recyclers = None
        self.__spawn_able_tiles = None
        self.__build_able_tiles = None
        self.__most_sided_bot = None


class Opponent(Player):
    def __init__(self):
        super().__init__(name='Opponent')


class Gamer(Player):
    def __init__(self, game):
        super().__init__(name='Gamer')
        self.actions = []
        self.isles = []
        self.strategy = Strategy(game)
        self.__optimal_move = None

    @property
    def str_actions(self):
        return [str(action) for action in self.actions]

    @property
    def optimal_move(self):
        if self.__optimal_move is None and self.side is not None:
            self.__optimal_move = (-1, 1)[self.side == 'left']
        return self.__optimal_move

    def setup(self, game):
        for bot in self.bots:
            bot.synchronize_with_others(self.bots)
        self.isles = [isle for isle in game.isles if ME in isle.owners]

    def play(self, game):
        self.setup(game)
        self.strategy.game = game
        for isle in self.isles:
            self.strategy.apply_to(isle)
        # LOGGER.append(f'MESSAGE impact: {game.impact} center: {self.center}')