import math
from entity.enemy.enemy import Enemy
from entity.projectile.boss_projectile import BossProjectile
from entity.loaders import load_sprite


class EnemyBoss(Enemy):

    def __init__(self, player, hp_scale=1.0, damage_scale=1.0):
        self.trans_frames, self.attack_frames = 11, 15
        self.idle_frames, self.smoke_frames, self.vanish_smoke_frames = 6, 8, 6
        self.hover_duration, self.descend_duration = 0.9, 1.1
        self.landing_duration, self.attack_duration = 0.6, 6.0
        self.vanish_duration, fire_cooldown = 0.7, 1.5
        self.hover_y_from_camera = 60
        self.fire_directions = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (0.7071, 0.7071),
            (-0.7071, 0.7071),
            (0.7071, -0.7071),
            (-0.7071, -0.7071),
        ]

        self.trans_sprite = None
        self.smoke_sprite = None
        self.vanish_smoke_sprite = None
        super().__init__(
            walk_sprite_path="assets/enemy/boss_idle.png",
            attack_sprite_path="assets/enemy/boss_attack.png",
            x=player.x,
            y=player.y,
            speed=0,
            max_health=320 * hp_scale,
            damage=25 * damage_scale,
            knockback_strength=0,
            walk_animation_duration=900,
            attack_animation_duration=1200,
            attack_duration=self.attack_duration,
            walk_frames=self.idle_frames,
            attack_frames=self.attack_frames,
            fire_cooldown=fire_cooldown,
        )
        self.state = "hovering"
        self.state_timer = self.hover_duration
        self.fire_timer = 0.0
        self.descend_target_x = self.descend_target_y = 0.0
        self.descend_dir_x = self.descend_dir_y = 0.0
        self.descend_speed = 0.0

    def setup_sprites(
        self,
        walk_sprite_path,
        attack_sprite_path,
        walk_frames,
        attack_frames,
        walk_animation_duration,
        attack_animation_duration,
    ):
        self.walk_sprite = load_sprite(walk_sprite_path, walk_frames, walk_animation_duration)
        self.attack_sprite = load_sprite(attack_sprite_path, attack_frames, attack_animation_duration)
        self.trans_sprite = load_sprite(
            "assets/enemy/boss_trans.png", self.trans_frames,
            int(self.descend_duration * 1000), loop=False,
        )
        self.smoke_sprite = load_sprite(
            "assets/fx/smoke_circular.png", self.smoke_frames,
            int(self.landing_duration * 1000), loop=False,
        )
        self.vanish_smoke_sprite = load_sprite(
            "assets/fx/boss_smoke.png", self.vanish_smoke_frames,
            int(self.vanish_duration * 1000), loop=False,
        )

    def change_state(self, state, duration, sprite=None):
        self.state = state
        self.state_timer = duration
        if sprite is not None:
            sprite.set_curr_frame(0)
            sprite.play()

    def update(self, target_x, target_y, enemies, dt, cam_x, cam_y, window, enemy_projectiles):
        self.state_timer = max(0, self.state_timer - dt)

        if self.state == "hovering":
            self.update_hovering(target_x, target_y, cam_y)
        elif self.state == "descending":
            self.update_descending(dt)
        elif self.state == "landing":
            self.update_landing()
        elif self.state == "attacking":
            self.update_attacking(dt, enemy_projectiles)
        elif self.state == "vanishing":
            self.update_vanishing()

        self.draw(cam_x, cam_y)
        if self.is_vulnerable():
            self.draw_health_bar(cam_x, cam_y, window)
        self.update_hit_effects(dt, cam_x, cam_y)

    def update_hovering(self, target_x, target_y, cam_y):
        self.x = target_x - self.width / 2
        self.y = cam_y + self.hover_y_from_camera - self.height / 2
        self.walk_sprite.update()
        if self.state_timer <= 0:
            # Tira uma "foto" da posicao do player e calcula a direcao reta ate
            # la. Como o alvo fica congelado, da para desviar saindo do lugar.
            self.descend_target_x = target_x - self.width / 2
            self.descend_target_y = target_y - self.height / 2
            dx = self.descend_target_x - self.x
            dy = self.descend_target_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                self.descend_dir_x = dx / dist
                self.descend_dir_y = dy / dist
            else:
                self.descend_dir_x = self.descend_dir_y = 0.0
            # Velocidade escolhida para cobrir a distancia dentro da duracao.
            self.descend_speed = dist / self.descend_duration
            self.change_state("descending", self.descend_duration, self.trans_sprite)

    def update_descending(self, dt):
        # Desce em linha reta no mesmo padrao do resto do jogo:
        # posicao += direcao * velocidade * dt.
        self.x += self.descend_dir_x * self.descend_speed * dt
        self.y += self.descend_dir_y * self.descend_speed * dt
        self.trans_sprite.update()
        if self.state_timer <= 0:
            # Encaixa no alvo para corrigir qualquer sobra de fracao de frame.
            self.x = self.descend_target_x
            self.y = self.descend_target_y
            self.change_state("landing", self.landing_duration, self.smoke_sprite)

    def update_landing(self):
        self.smoke_sprite.update()
        if self.state_timer <= 0:
            self.change_state("attacking", self.attack_duration)
            self.fire_timer = 0.0
            self.attack_sprite.set_curr_frame(0)

    def update_attacking(self, dt, enemy_projectiles):
        self.attack_sprite.update()
        self.fire_timer = max(0, self.fire_timer - dt)
        if self.fire_timer <= 0:
            self.fire_timer = self.fire_cooldown
            self.fire_salvo(enemy_projectiles)
        if self.state_timer <= 0:
            self.change_state("vanishing", self.vanish_duration, self.vanish_smoke_sprite)

    def update_vanishing(self):
        self.vanish_smoke_sprite.update()
        if self.state_timer <= 0:
            self.change_state("hovering", self.hover_duration)

    def fire_salvo(self, enemy_projectiles):
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        for dir_x, dir_y in self.fire_directions:
            enemy_projectiles.append(BossProjectile(center_x, center_y, dir_x, dir_y))

    def is_vulnerable(self):
        return self.state in ("landing", "attacking")

    def is_contact_active(self):
        return self.state in ("descending", "landing")

    def take_damage(self, amount, hit_dx, hit_dy):
        if not self.is_vulnerable():
            return
        super().take_damage(amount, hit_dx, hit_dy)

    def create_hit_effect(self):
        sprite, _, _, timer = super().create_hit_effect()
        return (sprite, self.x + self.width / 2, self.y + self.height / 2, timer)

    def collided(self, obj):
        if not self.is_contact_active():
            return False
        return super().collided(obj)

    def start_attack(self):
        return

    def current_sprite(self):
        if self.state == "hovering":
            return self.walk_sprite
        if self.state == "descending":
            return self.trans_sprite
        if self.state == "landing":
            return self.smoke_sprite
        if self.state == "vanishing":
            return self.vanish_smoke_sprite
        return self.attack_sprite

    def draw(self, camera_x, camera_y):
        sprite = self.current_sprite()
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        sprite.set_position(
            center_x - sprite.width / 2 - camera_x,
            center_y - sprite.height / 2 - camera_y,
        )
        sprite.draw()
