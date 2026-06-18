from entity.resource.resource import Resource


class GoldResource(Resource):

    def __init__(self, x, y):
        super().__init__("assets/resource/gold.png", x, y, 0.03, "Ouro", "assets/ui/icons/gold.png")
