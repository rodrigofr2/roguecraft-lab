# Carregamento de assets: centraliza a configuracao de Sprite e Sound (frames,
# duracao, volume, loop) que antes se repetia, igual, em cada artefato.
from PPlay.sprite import Sprite
from PPlay.sound import Sound


def load_sprite(path, frames, duration_ms, loop=True):
    sprite = Sprite(path, frames)
    sprite.set_total_duration(duration_ms)
    sprite.set_loop(loop)
    sprite.play()
    return sprite


def load_sound(path, volume, repeat=False):
    sound = Sound(path)
    sound.set_volume(volume)
    sound.set_repeat(repeat)
    return sound
