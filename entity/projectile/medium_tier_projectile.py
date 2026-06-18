from entity.projectile.projectile import Projectile
from entity.resource.crystal import CrystalResource
from entity.resource.iron import IronResource


class MediumTierProjectile(Projectile):

    def __init__(self, x, y, dir_x, dir_y):
        super().__init__(
            "assets/projectile/medium_tier.png",
            x, y, dir_x, dir_y,
            speed=320,
            damage=24,
            lifetime=1.9,
            display_name="Bomba Ninja",
            icon_path="assets/ui/icons/medium_tier_projectile.png",
            cost=[(CrystalResource, 2), (IronResource, 5)],
        )
