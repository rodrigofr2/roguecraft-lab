import math
from PPlay.gameobject import GameObject
from entity.loaders import load_sprite, load_sound


class Enemy(GameObject):

    def __init__(
        self,
        walk_sprite_path,
        attack_sprite_path,
        x,
        y,
        speed,
        max_health,
        damage,
        knockback_strength,
        walk_animation_duration,
        attack_animation_duration,
        attack_duration,
        walk_frames=4,
        attack_frames=4,
        hit_effect_duration=0.3,
        separation_radius=60,
        separation_force=0.6,
        attack_range=None,
        preferred_distance=0,
        fire_cooldown=0.0,
        projectile_class=None,
    ):
        GameObject.__init__(self)
        self.walk_sprite = None
        self.attack_sprite = None
        self.setup_sprites(
            walk_sprite_path,
            attack_sprite_path,
            walk_frames,
            attack_frames,
            walk_animation_duration,
            attack_animation_duration,
        )
        self.width = int(self.walk_sprite.width)
        self.height = int(self.walk_sprite.height)
        self.x = x
        self.y = y

        self.speed = speed
        self.health = max_health
        self.max_health = max_health
        self.damage = damage
        self.knockback_strength = knockback_strength
        self.separation_radius = separation_radius
        self.separation_force = separation_force
        self.hit_effect_duration = hit_effect_duration
        self.attack_range = attack_range
        self.preferred_distance = preferred_distance
        self.fire_cooldown = fire_cooldown
        self.fire_timer = 0.0
        self.projectile_class = projectile_class
        # Acelera quando o inimigo esta longe da tela, para nao ficar para tras do player.
        self.far_speed_radius = 175
        self.far_speed_multiplier = 1.75
        self.attack_timer = 0.0
        self.attack_duration = attack_duration
        self.is_moving = False
        self.hit_effects = []
        self.hit_sound = None
        self.setup_sounds()

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

    def setup_sounds(self):
        self.hit_sound = load_sound("assets/audio/hit.ogg", 35)

    def distance_to(self, target_x, target_y):
        # Distancia ate um ponto pelo teorema de Pitagoras: sqrt(dx^2 + dy^2).
        dx = target_x - self.x
        dy = target_y - self.y
        return math.sqrt(dx * dx + dy * dy)

    def get_effective_speed(self, target_x, target_y):
        # Longe da tela o inimigo acelera, para nao ficar para tras do player.
        if self.distance_to(target_x, target_y) > self.far_speed_radius:
            return self.speed * self.far_speed_multiplier
        return self.speed

    def move_towards(self, target_x, target_y, other_enemies, dt):
        effective_speed = self.get_effective_speed(target_x, target_y)

        # Direcao ate o player, transformada em vetor de comprimento 1.
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            dx /= dist
            dy /= dist

        # Inimigos a distancia (ranged): se chegaram perto demais, andam para
        # tras para manter a distancia preferida em vez de colar no player.
        if 0 < dist < self.preferred_distance:
            dx = -dx
            dy = -dy

        # Separacao: empurra para longe dos vizinhos muito proximos, para os
        # inimigos nao se amontoarem uns sobre os outros.
        for other in other_enemies:
            if other is self:
                continue
            ox = self.x - other.x
            oy = self.y - other.y
            odist = math.sqrt(ox * ox + oy * oy)
            if 0 < odist < self.separation_radius:
                dx += (ox / odist) * self.separation_force
                dy += (oy / odist) * self.separation_force

        # Normaliza de novo para a velocidade final ser sempre a mesma, nao
        # importa quantos vizinhos tenham empurrado o inimigo.
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length

        move_x = dx * effective_speed * dt
        move_y = dy * effective_speed * dt
        self.x += move_x
        self.y += move_y
        self.is_moving = move_x != 0 or move_y != 0

    def update(self, target_x, target_y, enemies, dt, cam_x, cam_y, window, enemy_projectiles):
        self.move_towards(target_x, target_y, enemies, dt)

        self.attack_timer = max(0, self.attack_timer - dt)
        if self.attack_timer > 0 or self.is_moving:
            self.current_sprite().update()
        else:
            self.walk_sprite.set_curr_frame(0)

        projectile = self.try_fire(target_x, target_y, dt)
        if projectile is not None:
            enemy_projectiles.append(projectile)

        self.draw(cam_x, cam_y)
        self.draw_health_bar(cam_x, cam_y, window)
        self.update_hit_effects(dt, cam_x, cam_y)

    def start_attack(self):
        self.attack_timer = self.attack_duration
        self.attack_sprite.set_curr_frame(0)

    def create_hit_effect(self):
        return (
            load_sprite(
                "assets/fx/enemy_hit.png", 4, int(self.hit_effect_duration * 1000), loop=False
            ),
            self.x,
            self.y,
            self.hit_effect_duration,
        )

    def take_damage(self, amount, hit_dx, hit_dy):
        self.health -= amount
        self.hit_sound.play()
        self.hit_effects.append(self.create_hit_effect())
        dist = math.sqrt(hit_dx * hit_dx + hit_dy * hit_dy)
        if dist > 0:
            self.x += (hit_dx / dist) * self.knockback_strength
            self.y += (hit_dy / dist) * self.knockback_strength

    def update_hit_effects(self, dt, cam_x, cam_y):
        active_effects = []
        for effect in self.hit_effects:
            sprite, x, y, timer = effect
            timer -= dt
            sprite.update()
            sprite.set_position(
                x - cam_x - sprite.width / 2,
                y - cam_y - sprite.height / 2,
            )
            sprite.draw()
            if timer > 0:
                active_effects.append((sprite, x, y, timer))
        self.hit_effects = active_effects

    def is_alive(self):
        return self.health > 0

    def current_sprite(self):
        # Enquanto o ataque esta ativo mostra o sprite de ataque; senao, o de andar.
        return self.attack_sprite if self.attack_timer > 0 else self.walk_sprite

    def draw(self, camera_x, camera_y):
        sprite = self.current_sprite()
        sprite.set_position(self.x - camera_x, self.y - camera_y)
        sprite.draw()

    def draw_health_bar(self, camera_x, camera_y, window):
        ratio = max(0, self.health / self.max_health)
        bar_w = self.width
        bar_x = self.x - camera_x
        bar_y = self.y - camera_y - 8

        if ratio > 0.6:
            color = (50, 200, 50)
        elif ratio > 0.3:
            color = (220, 200, 30)
        else:
            color = (220, 50, 50)

        total_blocks = max(1, bar_w // 6)
        filled_blocks = max(0, int(total_blocks * ratio))

        window.draw_text(
            "\u2588" * total_blocks, bar_x, bar_y, 10, (60, 60, 60)
        )
        if filled_blocks > 0:
            window.draw_text(
                "\u2588" * filled_blocks, bar_x, bar_y, 10, color
            )

    def try_fire(self, target_x, target_y, dt):
        if self.projectile_class is None:
            return None

        self.fire_timer = max(0, self.fire_timer - dt)
        if self.fire_timer > 0:
            return None

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist <= 0 or self.attack_range is None or dist > self.attack_range:
            return None

        self.fire_timer = self.fire_cooldown
        self.start_attack()
        return self.projectile_class(self.x, self.y, dx / dist, dy / dist)
