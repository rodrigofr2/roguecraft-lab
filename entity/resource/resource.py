from PPlay.gameobject import GameObject
from PPlay.gameimage import GameImage
from entity.loaders import load_sound


class Resource(GameObject):

    def __init__(self, sprite_path, x, y, spawn_chance, display_name, icon_path):
        GameObject.__init__(self)
        self.sprite = GameImage(sprite_path)
        self.width = self.sprite.width
        self.height = self.sprite.height
        self.x = x
        self.y = y
        self.collected = False
        self.spawn_chance = spawn_chance
        self.display_name = display_name
        self.icon_path = icon_path
        self.collect_sound = None
        self.setup_sounds()

    def setup_sounds(self):
        self.collect_sound = load_sound("assets/audio/collect.ogg", 30)

    def collect(self):
        self.collected = True
        self.collect_sound.play()

    def update(self, cam_x, cam_y):
        self.sprite.set_position(self.x - cam_x, self.y - cam_y)
        self.sprite.draw()
