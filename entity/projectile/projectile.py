from PPlay.gameobject import GameObject
from PPlay.gameimage import GameImage


class Projectile(GameObject):

    def __init__(self, sprite_path, x, y, dir_x, dir_y, speed, damage, lifetime, display_name, icon_path=None, cost=None):
        GameObject.__init__(self)
        self.sprite = GameImage(sprite_path)
        self.width = self.sprite.width
        self.height = self.sprite.height
        self.x = x
        self.y = y
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.speed = speed
        self.damage = damage
        self.lifetime = lifetime
        self.alive = True
        self.display_name = display_name
        self.icon_path = icon_path
        self.cost = cost if cost is not None else []

    def update(self, dt, cam_x, cam_y):
        self.x += self.dir_x * self.speed * dt
        self.y += self.dir_y * self.speed * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

        self.sprite.set_position(self.x - cam_x, self.y - cam_y)
        self.sprite.draw()
