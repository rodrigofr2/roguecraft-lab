from entity.passives.passive import Passive


class VitalityBlessing(Passive):

    def __init__(self):
        super().__init__("Benção da Vitalidade", "assets/ui/icons/vitality.png")

    def apply(self, player):
        player.max_health *= 1.10
