from PPlay.window import Window
from entity.player import Player
from entity.environment import EnvironmentRenderer
from entity.wave_manager import WaveManager
from entity.music_manager import MusicManager
from entity.hud import HUD

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 16
TILE_PADDING = 2

window = Window(SCREEN_WIDTH, SCREEN_HEIGHT)
window.set_title("RogueCraft")

keyboard = Window.get_keyboard()
mouse = Window.get_mouse()
environment = EnvironmentRenderer(SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, TILE_PADDING)


music_manager = MusicManager()


def reset_game():
    player = Player(0, 0)
    wave_manager = WaveManager(player, music_manager)
    return player, wave_manager


def start_run():
    global player, wave_manager, state
    player, wave_manager = reset_game()
    wave_manager.start_wave()
    state = "playing"

player, wave_manager = reset_game()
hud = HUD()
state = "menu"

while True:
    dt = window.delta_time()

    if keyboard.key_pressed("ESCAPE"):
        window.close()

    # A camera segue o player: o canto superior-esquerdo da tela, em coordenadas
    # de mundo, e a posicao do player menos meia tela. Tudo no mundo e desenhado
    # por "tela = mundo - cam"; so o player fica fixo no centro.
    cam_x = player.x - SCREEN_WIDTH / 2
    cam_y = player.y - SCREEN_HEIGHT / 2
    window.set_background_color([20, 20, 30])
    environment.update(dt, cam_x, cam_y)
    environment.draw(cam_x, cam_y)

    if state == "menu":
        player.draw(SCREEN_WIDTH, SCREEN_HEIGHT)
        hud.draw_main_menu(window, SCREEN_WIDTH, SCREEN_HEIGHT)

        if keyboard.key_pressed("ENTER"):
            start_run()

    elif state == "game_over":
        player.draw(SCREEN_WIDTH, SCREEN_HEIGHT)
        hud.draw_game_over(window, SCREEN_WIDTH, SCREEN_HEIGHT, wave_manager.wave_number)

        if keyboard.key_pressed("ENTER"):
            start_run()

    elif state in ("playing", "choosing"):
        state = wave_manager.update(
            dt, player, keyboard, mouse,
            SCREEN_WIDTH, SCREEN_HEIGHT, cam_x, cam_y, window,
        )

        hud.draw_playing(
            window, player.health, player.max_health,
            wave_manager.wave_number, player.inventory.get_resource_info(),
        )

        if player.inventory.last_crafted is not None:
            hud.show_craft_popup(player.inventory.last_crafted)
            player.inventory.last_crafted = None

        hud.draw_craft_popup(window, dt)

        if state == "choosing":
            state = wave_manager.update_choosing(player, hud, window, keyboard)

    window.update()
