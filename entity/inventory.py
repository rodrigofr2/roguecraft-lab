from entity.resource.wood import WoodResource
from entity.resource.stone import StoneResource
from entity.resource.iron import IronResource
from entity.resource.crystal import CrystalResource
from entity.resource.gold import GoldResource
from entity.projectile.basic_projectile import BasicProjectile
from entity.projectile.low_tier_projectile import LowTierProjectile
from entity.projectile.medium_tier_projectile import MediumTierProjectile
from entity.projectile.high_tier_projectile import HighTierProjectile


class ResourceStock:

    def __init__(self, resource):
        sample = resource(0, 0)
        self.resource = resource
        self.display_name = sample.display_name
        self.icon_path = sample.icon_path
        self.amount = 0


class Inventory:

    def __init__(self):
        self.resources = [
            ResourceStock(WoodResource),
            ResourceStock(StoneResource),
            ResourceStock(IronResource),
            ResourceStock(CrystalResource),
            ResourceStock(GoldResource),
        ]
        self.unlocked_resources = [WoodResource, StoneResource]
        self.blueprint = None
        self.equipped_projectile_class = BasicProjectile
        self.projectile_blueprints = [
            LowTierProjectile,
            MediumTierProjectile,
            HighTierProjectile,
        ]
        self.last_crafted = None

    def add_resource(self, resource):
        stock = self.find_stock(resource)
        if stock is not None:
            stock.amount += 1

    def collect_from(self, player, resources):
        for res in resources:
            if not res.collected and player.collided(res):
                res.collect()
                self.add_resource(type(res))
                self.try_auto_craft()

    def get_resource_info(self):
        return [
            (stock.display_name, stock.amount, stock.icon_path)
            for stock in self.resources
        ]

    def reset_resources(self):
        for stock in self.resources:
            stock.amount = 0

    def get_projectile(self):
        return self.equipped_projectile_class

    def unlock_resource(self, resource):
        if resource not in self.unlocked_resources:
            self.unlocked_resources.append(resource)

    def set_blueprint(self, projectile):
        self.blueprint = projectile
        self.try_auto_craft()

    def try_auto_craft(self):
        if self.blueprint is None:
            return False

        blueprint_instance = self.blueprint(0, 0, 1, 0)
        for resource_class, amount in blueprint_instance.cost:
            stock = self.find_stock(resource_class)
            if stock is None or stock.amount < amount:
                return False

        if self.equipped_projectile_class is not self.blueprint:
            self.last_crafted = self.blueprint
        self.equipped_projectile_class = self.blueprint
        return True

    def get_locked_resources(self):
        return [
            stock.resource
            for stock in self.resources
            if stock.resource not in self.unlocked_resources
        ]

    def find_stock(self, resource_class):
        for stock in self.resources:
            if stock.resource == resource_class:
                return stock
        return None
