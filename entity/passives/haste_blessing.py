from entity.passives.passive import Passive


class HasteBlessing(Passive):

    def __init__(self):
        super().__init__("Benção da Velocidade", "assets/ui/icons/haste.png")

    def apply(self, player):
        player.speed *= 1.02
