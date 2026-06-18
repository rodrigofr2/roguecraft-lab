from entity.resource.resource import Resource


class CrystalResource(Resource):

    def __init__(self, x, y):
        super().__init__("assets/resource/crystal.png", x, y, 0.05, "Cristal", "assets/ui/icons/crystal.png")
