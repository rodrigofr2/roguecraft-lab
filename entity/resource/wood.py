from entity.resource.resource import Resource


class WoodResource(Resource):

    def __init__(self, x, y):
        super().__init__("assets/resource/wood.png", x, y, 0.08, "Madeira", "assets/ui/icons/wood.png")
