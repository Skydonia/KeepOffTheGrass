import pandas as pd
import numpy as np
import operator
from .utils import get_tile_distances, get_most_sided_tile_from_list, get_recycling_scrap_infos
from .actions import Move, Spawn, Build
from .logger import LOGGER
from .const import RECYCLER_COST, BOT_COST, ME, NONE, OPP
from .bot_formation import ConquerFormation, CombatFormation, CleanFormation


class Player:
    def __init__(self, name: str):
        self.name = name
        self.tiles = []
        self.matter = 0
        self.spawned_recyclers = 0
        self.side = None
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
    def __init__(self):
        super().__init__(name='Gamer')
        self.actions = []
        self.formations = {}
        self.conquer = True
        self.__optimal_move = None

    @property
    def str_actions(self):
        return [str(action) for action in self.actions]

    @property
    def optimal_move(self):
        if self.__optimal_move is None and self.side is not None:
            self.__optimal_move = (-1, 1)[self.side == 'left']
        return self.__optimal_move

    @property
    def clean_formations(self):
        return [f for f in self.formations if 'clean' in f]

    @property
    def combat_formations(self):
        return [f for f in self.formations if 'combat' in f]

    def setup(self, game):
        for bot in self.bots:
            bot.synchronize_with_others(self.bots)
        if game.step == 1:
            self.formations['conquer'] = ConquerFormation(self, game)
            return
        for formation in self.formations:
            self.formations[formation].update(self, game)

    def bot_spawner(self, distances, bots: int = None, stack: any = 1):
        if len(distances) == 0:
            return
        if bots is None:
            bots = self.buildable_bots
        # LOGGER.append(f'MESSAGE max spawn: {min(bots, self.buildable_bots)}')
        bot_to_spawn = min(bots, self.buildable_bots)
        b = 0
        while (bot_to_spawn > 0) and (b < len(distances)):
            stack = -distances.iloc[b]['unit_gap']
            if stack < 0:
                stack = 0
            if bot_to_spawn >= stack > 0:
                self.actions.append(Spawn(stack, distances.iloc[b]['tile']))
                bot_to_spawn -= stack
            b += 1
        return

    def defend(self, game, bots: int = None, stack: any = 1):
        distances = get_tile_distances(self.bots, game.opponent.bots)
        distances = distances.sort_values('unit_gap')
        distances = distances[distances['unit_gap'] <= self.buildable_bots]
        self.bot_spawner(distances, bots, stack)

    def conquer(self, game, bots: int = None, stack: any = 1):
        distances = get_tile_distances(self.tiles, game.opponent.tiles)
        self.bot_spawner(distances, bots, stack)

    def cover(self, game, bots: int = None, stack: any = 1):
        distances_empty_tiles = get_tile_distances(self.tiles, game.neutral_tiles, by='empty_distance')
        distances_owned_bots = get_tile_distances(self.tiles, game.neutral_tiles, by='bot_distance', ascending=False)
        distances = pd.concat([distances_empty_tiles, distances_owned_bots])
        distances['compromise'] = distances_owned_bots['bot_distance'] - distances_empty_tiles['empty_distance']
        distances = distances.sort_values('compromise', ascending=False)
        self.bot_spawner(distances, bots, stack)

    def spawn_policy(self, game):
        # done = self.clean_formations
        # if done:
        #     return
        if not self.conquer:
            if len(self.clean_formations) > 0:
                for f in self.clean_formations:
                    self.formations[f].spawn()
            return
        distances = get_tile_distances(self.tiles, game.opponent.bots)
        if distances is None:
            return
        contact = distances[distances['distance'] <= 1]
        if len(contact) == 0:
            if self.matter > 30:
                if game.impact_step > 0:
                    self.backup_spawn(game, limit=0)
                    return
            self.backup_spawn(game, limit=30)
            # self.actions.append(Spawn(self.buildable_bots, self.most_sided_bot))
            return
        # self.bot_spawner(contact)
        if len(self.bots) > 0:
            self.defend(game)
        # if self.matter > 50 and len(self.clean_formations) == 0:
        if self.matter > 30:
            self.backup_spawn(game, limit=30)
            # self.actions.append(Spawn(self.buildable_bots, self.most_sided_bot))
            # self.matter -= BOT_COST
        return

    def backup_spawn(self, game, limit=30):
        op_distance = get_tile_distances(self.tiles, game.opponent.tiles)
        op_distance['unit_gap'] = -1
        self.bot_spawner(op_distance, bots=(self.matter - limit) // BOT_COST)
        return

    def prioritize_clean_formations(self):
        done = False
        for f in self.combat_formations + self.clean_formations:
            if self.combat_formations[f].isle.prioritize:
                self.formations[f].spawn()
                done = True
        return done

    def build_policy(self, game):
        # if game.step == 2:
        if 2 <= game.step <= 2 + max(game.first_impact_step // 2 - 1, 0):
            scrap_table = get_recycling_scrap_infos([tile for tile in self.tiles if tile.units == 0], game)
            self.actions.append(Build(scrap_table.iloc[0]['tile']))
        distances = get_tile_distances(self.build_able_tiles, game.opponent.bots)
        if distances is None:
            return
        d = distances[distances['distance'] <= 1]
        for tile in d['tile'].tolist():
            self.actions.append(Build(tile))
        return

    def move_policy(self, game):
        if game.isles_number > game.previous_isles_number:
            for isle in game.isles:
                # if ME in isle.owners and OPP in isle.owners:
                if isle.owners in [[ME, OPP], [OPP, ME]]:
                    combat = f'combat_{isle.id}'
                    if combat not in self.formations:
                        self.formations[combat] = CombatFormation(self, game, isle)
                    self.conquer = False
                if isle.owners == [ME]:
                    clean = f'clean_{isle.id}'
                    if clean not in self.formations:
                        self.formations[clean] = CleanFormation(self, game, isle)
        self.del_unused_formations()
        LOGGER.append(f'MESSAGE clean: {len(self.clean_formations)} combat: {len(self.combat_formations)}')
        for clean in self.clean_formations:
            self.formations[clean].move()

        for combat in self.combat_formations:
            self.formations[combat].move()

        if len(self.clean_formations) == 1:
            self.conquer = False

        if len(self.combat_formations) == 1:
            self.conquer = True

        if self.conquer:
            self.formations['conquer'].move()
        return

    def del_unused_formations(self):
        new_formation = {}
        for f in self.formations:
            if 'combat' in f and len(self.formations[f].isle.owners) < 2:
                continue
            if 'clean' in f and len(self.formations[f].isle.neutral_tiles) == 0:
                continue
            new_formation[f] = self.formations[f]
        self.formations = new_formation
