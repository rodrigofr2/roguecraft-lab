import random

from PPlay.gameimage import GameImage
from PPlay.window import Window
from entity.loaders import load_sound
from entity.passives.haste_blessing import HasteBlessing
from entity.passives.wrath_blessing import WrathBlessing
from entity.passives.vitality_blessing import VitalityBlessing
from entity.projectile.projectile import Projectile
from entity.resource.resource import Resource


class HUD:

    def __init__(self):
        self.current_choices = []
        self.choice_boxes = []
        self.choice_count = 3
        self.choice_width = 220
        self.choice_height = 110
        self.choice_gap = 24
        self.select_sound = None
        self.craft_popup_name = None
        self.craft_popup_timer = 0.0
        self.craft_popup_duration = 3.0
        self.icon_cache = {}
        self.setup_sounds()
        self.setup_images()

    def setup_sounds(self):
        self.select_sound = load_sound("assets/audio/select.ogg", 35)

    def setup_images(self):
        self.hud_panel = GameImage("assets/ui/hud_panel.png")
        self.choice_title_panel = GameImage("assets/ui/choice_title_panel.png")
        self.choice_card = GameImage("assets/ui/choice_card.png")
        self.game_over_panel = GameImage("assets/ui/game_over_panel.png")
        self.key_badge = GameImage("assets/ui/key_badge.png")
        self.resource_slot = GameImage("assets/ui/resource_slot.png")
        self.hp_under = GameImage("assets/ui/hp_under.png")
        self.hp_fill = GameImage("assets/ui/hp_fill.png")
        self.heart_icon = GameImage("assets/ui/icons/vitality.png")

    def get_icon(self, icon_path):
        if icon_path is None:
            return None
        if icon_path not in self.icon_cache:
            self.icon_cache[icon_path] = GameImage(icon_path)
        return self.icon_cache[icon_path]

    def draw_playing(self, window, health, max_health, wave_number, resource_info):
        display_health = int(health)
        display_max_health = int(max_health)
        ratio = max(0, min(1, display_health / max(1, display_max_health)))

        self.hud_panel.set_position(10, 10)
        self.hud_panel.draw()

        self.heart_icon.set_position(22, 18)
        self.heart_icon.draw()
        window.draw_text("Vida", 62, 22, 16, (72, 48, 26), bold=True)
        window.draw_text(
            f"{display_health}/{display_max_health}",
            62,
            42,
            14,
            (92, 53, 45),
            bold=True,
        )
        window.draw_text(f"Onda {wave_number}", 225, 24, 16, (72, 48, 26), bold=True)

        bar_x = 150
        bar_y = 44
        segment_count = 8
        filled_segments = int(round(segment_count * ratio))
        for index in range(segment_count):
            x = bar_x + index * 18
            self.hp_under.set_position(x, bar_y)
            self.hp_under.draw()
            if index < filled_segments:
                self.hp_fill.set_position(x, bar_y)
                self.hp_fill.draw()

        resource_start_x = 18
        resource_y = 58
        slot_gap = 62
        for index, (name, amount, icon_path) in enumerate(resource_info):
            slot_x = resource_start_x + index * slot_gap
            self.resource_slot.set_position(slot_x, resource_y)
            self.resource_slot.draw()

            icon = self.get_icon(icon_path)
            if icon is not None:
                icon.set_position(slot_x, resource_y)
                icon.draw()

            text_x = slot_x + 38
            amount_color = (66, 42, 22) if amount > 0 else (120, 110, 100)
            window.draw_text(str(amount), text_x, resource_y + 8, 16, amount_color, bold=True)

    def show_craft_popup(self, projectile_class):
        projectile = projectile_class(0, 0, 1, 0)
        self.craft_popup_name = projectile.display_name
        self.craft_popup_timer = self.craft_popup_duration
        if self.select_sound is not None:
            self.select_sound.play()

    def draw_craft_popup(self, window, dt):
        if self.craft_popup_name is None:
            return

        self.craft_popup_timer -= dt
        if self.craft_popup_timer <= 0:
            self.craft_popup_name = None
            return

        screen_w = Window.get_screen().get_width()
        panel_x = (screen_w - self.choice_card.width) // 2
        panel_y = 110
        self.choice_card.set_position(panel_x, panel_y)
        self.choice_card.draw()

        self.draw_centered_text(
            window, "Nova Arma Construída!", screen_w // 2, panel_y + 18, 16, (72, 48, 26), True,
        )
        self.draw_centered_text(
            window, self.craft_popup_name, screen_w // 2, panel_y + 54, 18, (166, 92, 38), True,
        )

    def draw_choosing(self, inventory, window, keyboard):
        if len(self.current_choices) == 0:
            self.current_choices = self.generate_choices(inventory)
            self.choice_boxes = self.build_choice_boxes()

        for index, choice in enumerate(self.current_choices):
            box_x, box_y, _, _ = self.choice_boxes[index]
            title, detail = self.describe_choice(choice)

            self.choice_card.set_position(box_x, box_y)
            self.choice_card.draw()

            self.key_badge.set_position(box_x + 12, box_y + 12)
            self.key_badge.draw()
            window.draw_text(str(index + 1), box_x + 21, box_y + 18, 14, (72, 48, 26), bold=True)

            icon = self.get_choice_icon(choice)
            if icon is not None:
                icon.set_position(box_x + 18, box_y + 44)
                icon.draw()

            window.draw_text(title, box_x + 60, box_y + 18, 15, (72, 48, 26), bold=True)

            for line_index, line in enumerate(self.wrap_text(detail, 22, 3)):
                window.draw_text(
                    line,
                    box_x + 60,
                    box_y + 46 + line_index * 16,
                    13,
                    (96, 62, 34),
                )

        keys = ["1", "2", "3"]
        for index, key in enumerate(keys):
            if index < len(self.current_choices) and keyboard.key_pressed(key):
                self.select_sound.play()
                choice = self.current_choices[index]
                self.current_choices = []
                self.choice_boxes = []
                return choice

        return None

    def draw_game_over(self, window, screen_w, screen_h, wave_number):
        panel_x = (screen_w - self.game_over_panel.width) // 2
        panel_y = (screen_h - self.game_over_panel.height) // 2

        self.game_over_panel.set_position(panel_x, panel_y)
        self.game_over_panel.draw()

        self.draw_centered_text(window, "GAME OVER", screen_w // 2, panel_y + 22, 28, (166, 52, 38), True)
        self.draw_centered_text(
            window,
            f"Onda Máxima: {wave_number}",
            screen_w // 2,
            panel_y + 64,
            18,
            (72, 48, 26),
            True,
        )
        self.draw_centered_text(
            window,
            "Pressione ENTER para tentar novamente!",
            screen_w // 2,
            panel_y + 92,
            14,
            (96, 62, 34),
        )

    def draw_main_menu(self, window, screen_w, screen_h):
        title_x = (screen_w - self.choice_title_panel.width) // 2
        title_y = 126
        panel_x = (screen_w - self.game_over_panel.width) // 2
        panel_y = 220

        self.choice_title_panel.set_position(title_x, title_y)
        self.choice_title_panel.draw()
        self.game_over_panel.set_position(panel_x, panel_y)
        self.game_over_panel.draw()

        self.draw_centered_text(window, "RogueCraft", screen_w // 2, title_y + 12, 26, (72, 48, 26), True)
        self.draw_centered_text(window, "Sobreviva as Ondas", screen_w // 2, panel_y + 28, 16, (72, 48, 26), True)
        self.draw_centered_text(window, "Controles: WASD e Mouse", screen_w // 2, panel_y + 58, 16, (96, 62, 34))
        self.draw_centered_text(window, "Pressione ENTER para iniciar", screen_w // 2, panel_y + 92, 16, (96, 62, 34), True)

    def generate_choices(self, inventory):
        # Pool de onde cada uma das 3 cartas e sorteada: blueprints de projetil,
        # recursos ainda bloqueados e as tres bencaos passivas.
        pool = list(inventory.projectile_blueprints)
        pool.extend(inventory.get_locked_resources())
        pool.append(HasteBlessing())
        pool.append(WrathBlessing())
        pool.append(VitalityBlessing())

        return [random.choice(pool) for _ in range(self.choice_count)]

    def build_choice_boxes(self):
        screen_w = Window.get_screen().get_width()
        start_x = (
            screen_w
            - (self.choice_width * self.choice_count + self.choice_gap * (self.choice_count - 1))
        ) // 2
        boxes = []
        for index in range(self.choice_count):
            boxes.append(
                (
                    start_x + index * (self.choice_width + self.choice_gap),
                    200,
                    self.choice_width,
                    self.choice_height,
                )
            )
        return boxes

    def describe_choice(self, choice):
        if hasattr(choice, "apply"):
            return choice.name, "Bônus Passivo Permanente"

        if issubclass(choice, Resource):
            return f"Desbloqueia {choice(0, 0).display_name}", "Recurso Disponível Para Coleta"

        # so resta projetil: o titulo e o nome e o detalhe e a lista de custo
        projectile = choice(0, 0, 1, 0)
        cost = ", ".join(
            f"{amount} {resource_class(0, 0).display_name}"
            for resource_class, amount in projectile.cost
        )
        return projectile.display_name, "Material necessário: " + cost

    def get_choice_icon(self, choice):
        if hasattr(choice, "apply"):
            return self.get_icon(choice.icon_path)

        if issubclass(choice, Resource):
            return self.get_icon(choice(0, 0).icon_path)

        if issubclass(choice, Projectile):
            return self.get_icon(choice(0, 0, 1, 0).icon_path)

        return None

    def wrap_text(self, text, max_chars, max_lines):
        words = text.split()
        lines = []
        current = ""

        for word in words:
            candidate = word if current == "" else current + " " + word
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
                if len(lines) == max_lines - 1:
                    break

        if len(lines) < max_lines and current:
            lines.append(current)

        if len(lines) > max_lines:
            lines = lines[:max_lines]

        if len(lines) == max_lines and len(" ".join(lines).split()) < len(words):
            if len(lines[-1]) > max_chars - 3:
                lines[-1] = lines[-1][:max_chars - 3].rstrip()
            lines[-1] += "..."

        return lines

    def draw_centered_text(self, window, text, center_x, y, size, color, bold=False):
        x = int(center_x - self.estimate_text_width(text, size) / 2)
        window.draw_text(text, x, y, size, color, bold=bold)

    def estimate_text_width(self, text, size):
        return len(text) * size * 0.58
