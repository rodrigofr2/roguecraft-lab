from entity.projectile.projectile import Projectile


class EnemyFastRangedProjectile(Projectile):

    def __init__(self, x, y, dir_x, dir_y):
        super().__init__(
            "assets/projectile/enemy_fast_ranged.png",
            x, y, dir_x, dir_y,
            speed=300,
            damage=7,
            lifetime=1.8,
            display_name="Enemy Fast Bolt",
            cost=[],
        )
