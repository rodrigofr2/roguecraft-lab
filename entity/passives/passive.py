class Passive:

    def __init__(self, name, icon_path):
        self.name = name
        self.icon_path = icon_path

    def apply(self, player):
        raise NotImplementedError()
