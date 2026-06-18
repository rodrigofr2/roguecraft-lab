from entity.projectile.projectile import Projectile
from entity.resource.wood import WoodResource
from entity.resource.stone import StoneResource


class LowTierProjectile(Projectile):

    def __init__(self, x, y, dir_x, dir_y):
        super().__init__(
            "assets/projectile/low_tier.png",
            x, y, dir_x, dir_y,
            speed=290,
            damage=16,
            lifetime=1.7,
            display_name="Magia de Fogo",
            icon_path="assets/ui/icons/low_tier_projectile.png",
            cost=[(WoodResource, 7), (StoneResource, 4)],
        )
