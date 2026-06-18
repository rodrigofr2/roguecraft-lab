from entity.projectile.projectile import Projectile


class EnemySlowRangedProjectile(Projectile):

    def __init__(self, x, y, dir_x, dir_y):
        super().__init__(
            "assets/projectile/enemy_slow_ranged.png",
            x, y, dir_x, dir_y,
            speed=170,
            damage=18,
            lifetime=2.6,
            display_name="Enemy Slow Bolt",
            cost=[],
        )
