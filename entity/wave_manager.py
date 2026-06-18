import random
import math
from entity.enemy.enemy_melee import EnemyMelee
from entity.enemy.enemy_slow_ranged import EnemySlowRanged
from entity.enemy.enemy_fast_ranged import EnemyFastRanged
from entity.enemy.enemy_boss import EnemyBoss


class WaveManager:

    def __init__(self, player, music_manager):
        self.wave_number = 0
        self.enemies = []
        self.enemy_projectiles = []
        self.resources = []
        self.wave_active = False
        self.player = player
        self.music_manager = music_manager

        self.enemies_to_spawn = 0
        self.enemies_alive = 0
        self.spawn_timer = 0.0
        self.is_boss_wave = False
        self.boss_spawned = False
        self._spawn_chances = {}

    def start_wave(self):
        self.wave_number += 1
        self.enemies = []
        self.enemy_projectiles = []
        self.resources = []
        self.wave_active = True
        self.is_boss_wave = self.wave_number % 5 == 0  # onda de boss a cada 5 ondas
        self.boss_spawned = False

        if self.is_boss_wave:
            self.enemies_to_spawn = 0
        else:
            self.enemies_to_spawn = self.wave_number * 3
        self.enemies_alive = 0
        self.spawn_timer = 0.0
        self.player.health = self.player.max_health
        self.music_manager.play_for_wave(self.wave_number)

    def update(self, dt, player, keyboard, mouse, screen_w, screen_h, cam_x, cam_y, window):
        # Sem onda ativa estamos na tela de escolha: so desenha o player e espera.
        if not self.wave_active:
            player.draw(screen_w, screen_h)
            return "choosing"

        # Spawn (boss substitui o spawn normal de inimigos), recursos e atualizacao
        # de cada inimigo da onda.
        if self.is_boss_wave:
            self.spawn_boss_if_needed(player)
        else:
            self.spawn_enemies(dt, player.x, player.y)
        self.spawn_resources(player, screen_w, cam_x, cam_y)

        for enemy in self.enemies:
            enemy.update(player.x, player.y, self.enemies, dt, cam_x, cam_y, window, self.enemy_projectiles)

        # Resolucao de colisoes: projeteis do player nos inimigos, contato dos
        # inimigos no player e projeteis inimigos no player.
        self.resolve_projectile_hits(player.projectiles)
        self.resolve_contact_damage(player)
        self.resolve_enemy_projectiles(player, dt, cam_x, cam_y)
        player.inventory.collect_from(player, self.resources)
        player.update(dt, keyboard, mouse, screen_w, screen_h, cam_x, cam_y, window)

        # Descarta o que saiu de cena: inimigos mortos, projeteis gastos e recursos
        # longe demais (margem de 10% caso o player queira voltar na regiao).
        self.enemies = [e for e in self.enemies if e.is_alive()]
        self.enemy_projectiles = [p for p in self.enemy_projectiles if p.alive]
        self.resources = [
            r for r in self.resources
            if not r.collected
            and abs(r.x - player.x) < (screen_w / 2) * 1.1
            and abs(r.y - player.y) < (screen_h / 2) * 1.1
        ]

        if not player.is_alive():
            return "game_over"

        if self.is_wave_cleared():
            player.inventory.reset_resources()
            self.resources = []
            self.enemy_projectiles = []
            self.wave_active = False
            return "choosing"

        return "playing"

    def is_wave_cleared(self):
        # Onda de boss acaba quando o boss ja nasceu e nao ha mais nada vivo;
        # onda normal acaba quando nao ha mais inimigos para spawnar nem vivos.
        if self.is_boss_wave:
            return self.boss_spawned and self.enemies_alive <= 0
        return self.enemies_to_spawn <= 0 and self.enemies_alive <= 0

    def update_choosing(self, player, hud, window, keyboard):
        choice = hud.draw_choosing(player.inventory, window, keyboard)
        if choice is None:
            return "choosing"

        player.apply_choice(choice)
        self.start_wave()
        return "playing"

    def spawn_enemies(self, dt, player_x, player_y):
        if self.enemies_to_spawn <= 0:
            return
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            # aumenta fator, tempo de spawn cresce mais rapidamente
            self.spawn_timer = 4 / (1 + 0.2 * (self.wave_number - 1))
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(300, 500)
            x = player_x + math.cos(angle) * dist
            y = player_y + math.sin(angle) * dist

            scale = 1 + (0.025 * self.wave_number)
            enemy = self.create_enemy(x, y, scale)

            self.enemies.append(enemy)
            self.enemies_to_spawn -= 1
            self.enemies_alive += 1

    def spawn_boss_if_needed(self, player):
        if self.boss_spawned:
            return
        scale = 1 + (0.0025 * self.wave_number)
        boss = EnemyBoss(player, hp_scale=scale, damage_scale=scale)
        self.enemies.append(boss)
        self.enemies_alive += 1
        self.boss_spawned = True

    def create_enemy(self, x, y, scale):
        if self.wave_number >= 5:
            types = [EnemyMelee, EnemySlowRanged, EnemyFastRanged]
            weights = [40, 35, 25]
        elif self.wave_number >= 3:
            types = [EnemyMelee, EnemySlowRanged]
            weights = [65, 35]
        else:
            return EnemyMelee(x, y, scale, scale, scale)

        enemy_class = random.choices(types, weights=weights, k=1)[0]
        return enemy_class(x, y, scale, scale, scale)

    def spawn_resources(self, player, screen_w, cam_x, cam_y):
        # So nascem recursos novos enquanto o player anda; parado, apenas redesenha.
        if player.is_moving:
            for res_type in player.inventory.unlocked_resources:
                if res_type not in self._spawn_chances:
                    self._spawn_chances[res_type] = res_type(0, 0).spawn_chance
                if random.random() < self._spawn_chances[res_type]:
                    angle = random.uniform(0, 2 * math.pi)
                    dist = random.uniform(screen_w / 2 + 10, screen_w)
                    x = player.x + math.cos(angle) * dist
                    y = player.y + math.sin(angle) * dist
                    self.resources.append(res_type(x, y))

        for res in self.resources:
            res.update(cam_x, cam_y)

    def resolve_projectile_hits(self, player_projectiles):
        for proj in player_projectiles:
            if not proj.alive:
                continue
            for enemy in self.enemies:
                if proj.collided(enemy):
                    enemy.take_damage(proj.damage, enemy.x - proj.x, enemy.y - proj.y)
                    proj.alive = False
                    if not enemy.is_alive():
                        self.enemies_alive -= 1
                    break

    def resolve_contact_damage(self, player):
        for enemy in self.enemies:
            if enemy.is_alive() and enemy.collided(player):
                player.take_damage(enemy.damage)
                enemy.start_attack()

    def resolve_enemy_projectiles(self, player, dt, cam_x, cam_y):
        for projectile in self.enemy_projectiles:
            if not projectile.alive:
                continue
            projectile.update(dt, cam_x, cam_y)
            if projectile.collided(player):
                player.take_damage(projectile.damage)
                projectile.alive = False
