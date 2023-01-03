from .bot_formation import ConquerFormation, CombatFormation, CleanFormation
from .const import ME, OPP


class Strategy:
    def __init__(self, game):
        self.game = game
        self.formations = {}

    @property
    def player(self):
        return self.game.gamer

    @property
    def step(self):
        return self.game.step

    @staticmethod
    def find_adapted_formation(isle):
        if isle.owners == [ME]:
            if len(isle.neutral_tiles) == 0:
                return None
            return CleanFormation
        if isle.owners in [[ME, OPP], [OPP, ME]] and len(isle.gamer_tiles) < len(isle.opponent_tiles) // 5:
            return CombatFormation
        return ConquerFormation

    def apply_to(self, isle):
        adapted_formation = self.find_adapted_formation(isle)
        if adapted_formation is None:
            if isle.id in self.formations:
                del self.formations[isle.id]
            return
        self.set_adapted_formation(adapted_formation, isle)
        self.formations[isle.id].build()
        self.formations[isle.id].spawn()
        self.formations[isle.id].move()
        return

    def set_adapted_formation(self, adapted_formation, isle):
        if isle.id in self.formations:
            if type(self.formations[isle.id]) == adapted_formation:
                self.formations[isle.id].update(self.player, self.game, isle)
                return
        self.formations[isle.id] = adapted_formation(self.player, self.game, isle)
        return
