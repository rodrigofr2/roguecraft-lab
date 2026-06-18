from entity.loaders import load_sound


class MusicManager:

    def __init__(self):
        self.theme_track = load_sound("assets/audio/bgm.ogg", 20, repeat=True)
        self.fight_track = load_sound("assets/audio/fight.ogg", 20, repeat=True)
        self.boss_track = load_sound("assets/audio/final_area.ogg", 25, repeat=True)
        self.current_track = self.theme_track

    def play_for_wave(self, wave_number):
        # Para a faixa atual e escolhe a trilha conforme a fase da partida:
        # boss a cada 5 ondas, tema calmo nas duas primeiras, combate nas demais.
        self.current_track.stop()
        if wave_number % 5 == 0:
            self.current_track = self.boss_track
        elif wave_number < 3:
            self.current_track = self.theme_track
        else:
            self.current_track = self.fight_track
        self.current_track.play()
