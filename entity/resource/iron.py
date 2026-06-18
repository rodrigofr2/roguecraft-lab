from entity.resource.resource import Resource


class IronResource(Resource):

    def __init__(self, x, y):
        super().__init__("assets/resource/iron.png", x, y, 0.05, "Ferro", "assets/ui/icons/iron.png")
