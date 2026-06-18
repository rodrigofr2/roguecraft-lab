from entity.passives.passive import Passive


class WrathBlessing(Passive):

    def __init__(self):
        super().__init__("Benção da Fúria", "assets/ui/icons/wrath.png")

    def apply(self, player):
        player.damage_bonus += 2
