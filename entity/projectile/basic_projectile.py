from entity.projectile.projectile import Projectile


class BasicProjectile(Projectile):

    def __init__(self, x, y, dir_x, dir_y):
        super().__init__(
            "assets/projectile/basic.png",
            x, y, dir_x, dir_y,
            speed=250,
            damage=15,
            lifetime=1.5,
            display_name="Basic",
            icon_path="assets/ui/icons/basic_projectile.png",
            cost=[],
        )
