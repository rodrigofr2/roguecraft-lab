from entity.resource.resource import Resource


class StoneResource(Resource):

    def __init__(self, x, y):
        super().__init__("assets/resource/stone.png", x, y, 0.06, "Pedra", "assets/ui/icons/stone.png")
