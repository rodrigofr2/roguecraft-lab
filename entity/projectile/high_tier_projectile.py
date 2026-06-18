from entity.projectile.projectile import Projectile
from entity.resource.gold import GoldResource
from entity.resource.crystal import CrystalResource


class HighTierProjectile(Projectile):

    def __init__(self, x, y, dir_x, dir_y):
        super().__init__(
            "assets/projectile/high_tier.png",
            x, y, dir_x, dir_y,
            speed=360,
            damage=36,
            lifetime=2.1,
            display_name="Shuriken Superior",
            icon_path="assets/ui/icons/high_tier_projectile.png",
            cost=[(GoldResource, 2), (CrystalResource, 5)],
        )
