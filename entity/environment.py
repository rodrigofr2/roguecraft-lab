import random

from PPlay.gameimage import GameImage
from entity.loaders import load_sprite


class RainDrop:
    def __init__(self, x, y, speed, ground_y):
        self.x = x
        self.y = y
        self.speed = speed
        self.ground_y = ground_y  # altura (no mundo) onde a gota respinga


class RainSplash:
    def __init__(self, x, y, timer):
        self.x = x
        self.y = y
        self.timer = timer  # tempo restante ate o respingo sumir


class EnvironmentRenderer:
    def __init__(self, screen_w, screen_h, tile_size, tile_padding):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.tile_size = tile_size
        self.tile_padding = tile_padding
        self.floor_tile = GameImage("assets/tiles/floor.png")

        self.bushes = [
            GameImage("assets/environment/bush_a.png"),
            GameImage("assets/environment/bush_b.png"),
        ]
        self.foliage = [
            GameImage("assets/environment/foliage_a.png"),
            GameImage("assets/environment/foliage_b.png"),
            GameImage("assets/environment/foliage_c.png"),
            GameImage("assets/environment/foliage_d.png"),
        ]
        self.flowers = [
            GameImage("assets/environment/flower_a.png"),
            GameImage("assets/environment/flower_b.png"),
            GameImage("assets/environment/flower_c.png"),
        ]
        self.sprouts = [
            GameImage("assets/environment/sprout_a.png"),
        ]

        # O que nasce em cada tile e decidido uma unica vez (na primeira vez que
        # o tile aparece) e guardado aqui. Assim a mesma decoracao reaparece no
        # mesmo lugar quando o player volta, sem recalcular nem sortear de novo.
        # Cada valor e a imagem da decoracao ou None quando o tile fica pelado.
        self.decorations = {}
        # Posicoes que ja receberam uma moita, usado para nao colocar duas moitas
        # coladas uma na outra.
        self.bush_tiles = set()

        self.rain_sprite = load_sprite("assets/environment/rain.png", 3, 320)
        self.rain_splash_sprite = load_sprite("assets/environment/rain_on_floor.png", 3, 260)
        self.rain_count = 35
        self.rain_speed_min = 360
        self.rain_speed_max = 560
        self.splash_duration = 0.35
        self.rain_drops = [self.create_raindrop(0, 0) for _ in range(self.rain_count)]
        self.rain_splashes = []

    def create_raindrop(self, cam_x, cam_y):
        # Uma gota de chuva em coordenadas de MUNDO, sorteada dentro da area
        # visivel (ao redor da camera) para que a chuva sempre cubra a tela e
        # fique presa ao mundo, nao ao player. A gota comeca acima da altura de
        # respingo e cai em linha reta ate la.
        ground_y = cam_y + random.uniform(0, self.screen_h)
        return RainDrop(
            cam_x + random.uniform(0, self.screen_w),
            ground_y - random.uniform(20, self.screen_h),
            random.uniform(self.rain_speed_min, self.rain_speed_max),
            ground_y,
        )

    def update(self, dt, cam_x, cam_y):
        self.rain_sprite.update()
        self.rain_splash_sprite.update()

        for i, drop in enumerate(self.rain_drops):
            drop.y += drop.speed * dt
            if drop.y >= drop.ground_y:
                # Tocou o chao: deixa um respingo e a gota recomeca perto da
                # camera (assim a chuva continua cobrindo a tela conforme o
                # player anda pelo mundo).
                self.rain_splashes.append(RainSplash(drop.x, drop.ground_y, self.splash_duration))
                self.rain_drops[i] = self.create_raindrop(cam_x, cam_y)

        # Envelhece os respingos e descarta os que ja terminaram.
        for splash in self.rain_splashes:
            splash.timer -= dt
        self.rain_splashes = [s for s in self.rain_splashes if s.timer > 0]

    def draw(self, cam_x, cam_y):
        left = int(cam_x) // self.tile_size - self.tile_padding
        right = int(cam_x + self.screen_w) // self.tile_size + self.tile_padding
        top = int(cam_y) // self.tile_size - self.tile_padding
        bottom = int(cam_y + self.screen_h) // self.tile_size + self.tile_padding

        for ty in range(top, bottom + 1):
            for tx in range(left, right + 1):
                sx = tx * self.tile_size - cam_x
                sy = ty * self.tile_size - cam_y

                self.floor_tile.set_position(sx, sy)
                self.floor_tile.draw()

                decoration = self.decoration_for(tx, ty)
                if decoration is None:
                    continue

                decoration.set_position(sx, sy)
                decoration.draw()

        self.draw_rain(cam_x, cam_y)

    def draw_rain(self, cam_x, cam_y):
        # A chuva vive no mundo; na tela cada gota aparece em "mundo - camera".
        for drop in self.rain_drops:
            self.rain_sprite.set_position(drop.x - cam_x, drop.y - cam_y)
            self.rain_sprite.draw()

        for splash in self.rain_splashes:
            self.rain_splash_sprite.set_position(splash.x - cam_x, splash.y - cam_y)
            self.rain_splash_sprite.draw()

    def decoration_for(self, tx, ty):
        # Decide o que tem no tile so na primeira vez e guarda a resposta, para
        # reaproveitar nas proximas vezes (a decoracao nao muda a cada frame).
        if (tx, ty) not in self.decorations:
            self.decorations[(tx, ty)] = self.roll_decoration(tx, ty)
        return self.decorations[(tx, ty)]

    def roll_decoration(self, tx, ty):
        # Sorteio simples: um numero entre 0 e 1 escolhe o que nasce no tile.
        # As faixas vao do mais raro (moita) ao mais comum (broto); o resto fica
        # como chao pelado.
        roll = random.random()

        if roll < 0.015:
            # Moita: so nasce se nao houver outra moita colada (evita aglomerado).
            if self.has_bush_neighbor(tx, ty):
                return None
            self.bush_tiles.add((tx, ty))
            return random.choice(self.bushes)
        if roll < 0.06:
            return random.choice(self.foliage)
        if roll < 0.10:
            return random.choice(self.flowers)
        if roll < 0.14:
            return random.choice(self.sprouts)

        return None

    def has_bush_neighbor(self, tx, ty):
        # Olha os quatro tiles vizinhos: se algum ja tem moita, este fica sem.
        for nx, ny in ((tx - 1, ty), (tx + 1, ty), (tx, ty - 1), (tx, ty + 1)):
            if (nx, ny) in self.bush_tiles:
                return True
        return False
