import math
from PPlay.gameobject import GameObject
from entity.loaders import load_sprite, load_sound
from entity.inventory import Inventory
from entity.projectile.projectile import Projectile
from entity.resource.resource import Resource
from entity.passives.passive import Passive


class Player(GameObject):

    def __init__(self, x, y):
        GameObject.__init__(self)

        self.sprites = {}
        self.attack_sprites = {}
        self.dash_sprite = None
        self.hit_sprite = None
        self.setup_sprites()

        self.width = int(self.sprites["down"].width)
        self.height = int(self.sprites["down"].height)
        self.x = x
        self.y = y

        self.speed = 100
        self.health = 100
        self.max_health = 100
        self.damage_bonus = 0
        self.facing = "down"
        self.fire_cooldown = 0.75
        self.fire_timer = 0.0
        self.attack_timer = 0.0
        self.hit_timer = 0.0
        self.invuln_duration = 0.8
        self.invuln_timer = 0.0
        self.dash_distance = 75
        self.dash_duration = 0.18
        self.dash_cooldown = 2.5
        self.dash_timer = 0.0
        self.dash_cooldown_timer = 0.0
        self.dash_dx = 0.0
        self.dash_dy = 1.0
        self.attack_sound = None
        self.hit_sound = None
        self.dash_sound = None
        self.setup_sounds()

        self.is_moving = False
        self.inventory = Inventory()
        self.projectiles = []
        self.was_firing = False
        self.is_charging = False
        self.charge_timer = 0.0
        # Cada faixa de tempo segurado da um multiplicador (e uma cor na barra).
        self.charge_thresholds = [1.0, 1.5, 2.0, 2.5, 3.0]
        self.charge_multipliers = [1.1, 1.5, 2.0, 2.5, 3.0]
        self.charge_colors = [
            (120, 200, 255),
            (90, 220, 120),
            (240, 220, 60),
            (245, 150, 40),
            (235, 60, 50),
        ]

    def setup_sprites(self):
        self.sprites = {
            "up": load_sprite("assets/player/walk_up.png", 4, 400),
            "down": load_sprite("assets/player/walk_down.png", 4, 400),
            "left": load_sprite("assets/player/walk_left.png", 4, 400),
            "right": load_sprite("assets/player/walk_right.png", 4, 400),
        }
        self.attack_sprites = {
            "up": load_sprite("assets/player/attack_up.png", 4, 350),
            "down": load_sprite("assets/player/attack_down.png", 4, 350),
            "left": load_sprite("assets/player/attack_left.png", 4, 350),
            "right": load_sprite("assets/player/attack_right.png", 4, 350),
        }
        self.dash_sprite = load_sprite("assets/player/dash.png", 1, 180)
        self.hit_sprite = load_sprite("assets/fx/player_hit.png", 1, 250)

    def setup_sounds(self):
        self.attack_sound = load_sound("assets/audio/attack.ogg", 35)
        self.hit_sound = load_sound("assets/audio/player_hit.ogg", 35)
        self.dash_sound = load_sound("assets/audio/dash.wav", 45)

    def update(self, dt, keyboard, mouse, screen_w, screen_h, cam_x, cam_y, window):
        self.dash(dt, keyboard)
        self.move(dt, keyboard)
        self.attack(dt, mouse, screen_w, screen_h, cam_x, cam_y, window)
        self.draw(screen_w, screen_h)

    def read_movement_input(self, keyboard):
        # Le WASD e devolve a direcao (dx, dy). Usado tanto pelo andar quanto
        # pelo dash, para que as duas acoes interpretem o teclado da mesma forma.
        dx = 0
        dy = 0
        if keyboard.key_pressed("A"):
            dx -= 1
        if keyboard.key_pressed("D"):
            dx += 1
        if keyboard.key_pressed("W"):
            dy -= 1
        if keyboard.key_pressed("S"):
            dy += 1

        if dx != 0 and dy != 0:
            # 0.7071 ~= 1/raiz(2): normaliza a diagonal para nao andar mais
            # rapido do que andar em linha reta.
            dx *= 0.7071
            dy *= 0.7071
        return dx, dy

    def facing_vector(self):
        if self.facing == "up":
            return 0, -1
        if self.facing == "down":
            return 0, 1
        if self.facing == "left":
            return -1, 0
        return 1, 0

    def dash(self, dt, keyboard):
        self.dash_cooldown_timer = max(0, self.dash_cooldown_timer - dt)

        if self.dash_timer > 0:
            speed = self.dash_distance / self.dash_duration
            self.x += self.dash_dx * speed * dt
            self.y += self.dash_dy * speed * dt
            self.dash_timer = max(0, self.dash_timer - dt)
        elif keyboard.key_pressed("space") and self.dash_cooldown_timer <= 0 and not self.is_charging:
            dx, dy = self.read_movement_input(keyboard)
            if dx == 0 and dy == 0:
                # Sem direcao apertada: o dash sai para onde o player encara.
                dx, dy = self.facing_vector()
            self.dash_dx = dx
            self.dash_dy = dy
            self.dash_timer = self.dash_duration
            self.dash_cooldown_timer = self.dash_cooldown
            self.dash_sound.play()

    def move(self, dt, keyboard):
        if self.dash_timer > 0 or self.is_charging:
            self.is_moving = False
            return

        move_x, move_y = self.read_movement_input(keyboard)
        dx = move_x * self.speed * dt
        dy = move_y * self.speed * dt

        if self.attack_timer > 0:
            self.is_moving = False
        elif dx != 0 or dy != 0:
            self.is_moving = True
            if abs(dx) > abs(dy):
                self.facing = "right" if dx > 0 else "left"
            else:
                self.facing = "down" if dy > 0 else "up"
            self.x += dx
            self.y += dy
        else:
            self.is_moving = False

    def aim_direction(self, mouse, screen_w, screen_h):
        mouse_x, mouse_y = mouse.get_position()
        aim_dx = mouse_x - screen_w / 2
        aim_dy = mouse_y - screen_h / 2
        aim_dist = math.hypot(aim_dx, aim_dy)
        if aim_dist <= 0:
            return None
        if abs(aim_dx) > abs(aim_dy):
            self.facing = "right" if aim_dx > 0 else "left"
        else:
            self.facing = "down" if aim_dy > 0 else "up"
        return aim_dx / aim_dist, aim_dy / aim_dist

    def attack(self, dt, mouse, screen_w, screen_h, cam_x, cam_y, window):
        firing = mouse.is_button_pressed(1)
        if firing:
            # Segurando: acumula a carga. Depois de passar o cooldown de clique a
            # carga "engata" (a barra aparece) e o player passa a mirar no cursor.
            self.charge_timer += dt
            if self.charge_timer >= self.fire_cooldown:
                self.is_charging = True
                self.aim_direction(mouse, screen_w, screen_h)
        elif self.was_firing and self.fire_timer <= 0:
            # Soltou o botao: carga longa vira o tiro carregado; clique rapido
            # (sem ter engatado a carga) vira o ataque normal.
            aim = self.aim_direction(mouse, screen_w, screen_h)
            if aim is not None:
                if self.is_charging:
                    self.special_attack(aim)
                else:
                    self.fire_projectile(aim, 1.0)

        if not firing:
            self.charge_timer = 0.0
            self.is_charging = False
        self.was_firing = firing

        self.fire_timer = max(0, self.fire_timer - dt)
        self.attack_timer = max(0, self.attack_timer - dt)
        self.hit_timer = max(0, self.hit_timer - dt)
        self.invuln_timer = max(0, self.invuln_timer - dt)

        self.animate_current_sprite()
        self.draw_special_attack_bar(window, screen_w, screen_h)

        for proj in self.projectiles:
            proj.update(dt, cam_x, cam_y)
        self.projectiles = [p for p in self.projectiles if p.alive]

    def fire_projectile(self, aim, factor):
        # Dispara o projetil equipado na direcao mirada. O fator multiplica o
        # dano; com fator 1.0 e o tiro normal, acima disso e a versao carregada.
        aim_dx, aim_dy = aim
        proj_class = self.inventory.get_projectile()
        projectile = proj_class(self.x, self.y, aim_dx, aim_dy)
        projectile.damage = (projectile.damage + self.damage_bonus) * factor
        self.fire_timer = self.fire_cooldown
        self.attack_timer = 0.35
        self.projectiles.append(projectile)
        self.attack_sound.play()

    def current_sprite(self):
        # Prioridade visual: dash/carga > levar dano > atacar > andar/parado.
        if self.dash_timer > 0 or self.is_charging:
            return self.dash_sprite
        if self.hit_timer > 0:
            return self.hit_sprite
        if self.attack_timer > 0:
            return self.attack_sprites[self.facing]
        return self.sprites[self.facing]

    def animate_current_sprite(self):
        sprite = self.current_sprite()
        # Apenas o sprite de andar fica parado no frame 0 quando o player esta
        # parado; nos demais estados (dash, hit, ataque) a animacao sempre corre.
        idle_walk = (
            self.dash_timer <= 0
            and self.hit_timer <= 0
            and self.attack_timer <= 0
            and not self.is_moving
        )
        if idle_walk:
            sprite.set_curr_frame(0)
        else:
            sprite.update()

    def take_damage(self, amount):
        if self.invuln_timer > 0:
            return
        self.health -= amount
        self.hit_sound.play()
        self.hit_timer = 0.25
        self.invuln_timer = self.invuln_duration

    def apply_choice(self, choice):
        # Passive ja vem instanciada (tem efeito proprio); projetil e recurso
        # chegam como CLASSE, pois so serao instanciados quando usados/spawnados.
        if isinstance(choice, Passive):
            choice.apply(self)
        elif issubclass(choice, Projectile):
            self.inventory.set_blueprint(choice)
        elif issubclass(choice, Resource):
            self.inventory.unlock_resource(choice)

    def is_alive(self):
        return self.health > 0

    def draw(self, screen_w, screen_h):
        sprite = self.current_sprite()
        sprite.set_position(screen_w / 2 - self.width / 2, screen_h / 2 - self.height / 2)
        # Durante os i-frames o player pisca: ~10x por segundo ele alterna entre
        # desenhar e pular o desenho.
        if self.invuln_timer > 0 and int(self.invuln_timer * 20) % 2 == 0:
            return
        sprite.draw()

    def charge_level(self):
        # Faixa de carga atual (indice 0..n-1) conforme o tempo segurado; acima
        # da ultima faixa fica na maior. E a fonte unica do nivel de carga: o
        # multiplicador de dano e a cor/tamanho da barra saem todos daqui.
        for index, threshold in enumerate(self.charge_thresholds):
            if self.charge_timer < threshold:
                return index
        return len(self.charge_multipliers) - 1

    def charge_factor(self):
        return self.charge_multipliers[self.charge_level()]

    def draw_special_attack_bar(self, window, screen_w, screen_h):
        if not self.is_charging:
            return

        level = self.charge_level()
        color = self.charge_colors[level]
        filled_blocks = level + 1

        total_blocks = len(self.charge_multipliers)
        bar_x = screen_w / 2 - self.width / 2
        bar_y = screen_h / 2 - self.height / 2 - 8

        window.draw_text("\u2588" * total_blocks, bar_x, bar_y, 10, (60, 60, 60))
        window.draw_text("\u2588" * filled_blocks, bar_x, bar_y, 10, color)

    def rotate_aim(self, aim, angle):
        # Gira o vetor de mira (ja normalizado) por um angulo em radianos.
        # Como o vetor de origem e unitario, o resultado tambem e, entao serve
        # direto como direcao para fire_projectile.
        aim_dx, aim_dy = aim
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return (
            aim_dx * cos_a - aim_dy * sin_a,
            aim_dx * sin_a + aim_dy * cos_a,
        )

    def special_attack(self, aim):
        # Mesma semantica do tiro carregado, mas em leque: alem do projetil
        # central, dois laterais inclinados formam um triangulo de disparo.
        factor = self.charge_factor()
        spread = math.radians(15)
        for angle in (-spread, 0.0, spread):
            self.fire_projectile(self.rotate_aim(aim, angle), factor)