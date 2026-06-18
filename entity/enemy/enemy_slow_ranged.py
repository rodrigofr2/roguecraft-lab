from entity.enemy.enemy import Enemy
from entity.projectile.enemy_slow_ranged_projectile import EnemySlowRangedProjectile


class EnemySlowRanged(Enemy):

    def __init__(self, x, y, hp_scale=1.0, speed_scale=1.0, damage_scale=1.0):
        super().__init__(
            walk_sprite_path="assets/enemy/slow_ranged.png",
            attack_sprite_path="assets/enemy/slow_ranged_attack.png",
            x=x,
            y=y,
            speed=52 * speed_scale,
            max_health=50 * hp_scale,
            damage=10 * damage_scale,
            knockback_strength=12,
            walk_animation_duration=480,
            attack_animation_duration=300,
            attack_duration=0.30,
            attack_range=220,
            fire_cooldown=1.8,
            projectile_class=EnemySlowRangedProjectile,
            preferred_distance=220,
        )
