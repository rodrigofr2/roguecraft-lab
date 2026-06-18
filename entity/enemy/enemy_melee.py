from entity.enemy.enemy import Enemy


class EnemyMelee(Enemy):

    def __init__(self, x, y, hp_scale=1.0, speed_scale=1.0, damage_scale=1.0):
        super().__init__(
            walk_sprite_path="assets/enemy/melee.png",
            attack_sprite_path="assets/enemy/melee_attack.png",
            x=x,
            y=y,
            speed=60 * speed_scale,
            max_health=30 * hp_scale,
            damage=20 * damage_scale,
            knockback_strength=10,
            walk_animation_duration=420,
            attack_animation_duration=240,
            attack_duration=0.20,
            preferred_distance=20,
        )
