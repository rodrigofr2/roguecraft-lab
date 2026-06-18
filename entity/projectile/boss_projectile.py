from entity.projectile.projectile import Projectile


class BossProjectile(Projectile):

    def __init__(self, x, y, dir_x, dir_y):
        super().__init__(
            "assets/projectile/boss_dynamite.png",
            x, y, dir_x, dir_y,
            speed=190,
            damage=18,
            lifetime=3.2,
            display_name="Boss Dynamite",
            cost=[],
        )
