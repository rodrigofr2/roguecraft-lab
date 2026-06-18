from entity.enemy.enemy import Enemy
from entity.projectile.enemy_fast_ranged_projectile import EnemyFastRangedProjectile


class EnemyFastRanged(Enemy):

    def __init__(self, x, y, hp_scale=1.0, speed_scale=1.0, damage_scale=1.0):
        super().__init__(
            walk_sprite_path="assets/enemy/fast_ranged.png",
            attack_sprite_path="assets/enemy/fast_ranged_attack.png",
            x=x,
            y=y,
            speed=35 * speed_scale,
            max_health=26 * hp_scale,
            damage=7 * damage_scale,
            knockback_strength=22,
            walk_animation_duration=300,
            attack_animation_duration=180,
            attack_duration=0.16,
            attack_range=300,
            fire_cooldown=0.8,
            projectile_class=EnemyFastRangedProjectile,
            preferred_distance=300,
        )
