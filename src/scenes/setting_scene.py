'''
[TODO HACKATHON 5]
Try to mimic the menu_scene.py or game_scene.py to create this new scene
'''

import pygame as pg

from src.utils import GameSettings
from src.sprites import BackgroundSprite, Sprite
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from typing import override


class SettingScene(Scene):
    def __init__(self):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.font_title = pg.font.Font("assets/fonts/Minecraft.ttf", 40)
        self.font_text = pg.font.Font("assets/fonts/Minecraft.ttf", 20)

        px,py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2

      
        self.panel_img = pg.image.load("assets/images/ui/raw/UI_Flat_Frame03a.png").convert_alpha()
        self.panel_img = pg.transform.smoothscale(self.panel_img, (550, 400))
        self.panel_rect = self.panel_img.get_rect(center=(px,py))

   
        self.slider_rect = pg.Rect(self.panel_rect.left + 100, self.panel_rect.top + 130, 350, 16)
        self.knob_rect = pg.Rect(0, 0, 20, 28)
        self.dragging = False
        self.update_knob_position()

        self.muted = False
        self._last_volume_before_mute = GameSettings.AUDIO_VOLUME

     
        self.mute_button = Button(
            "ui/raw/UI_Flat_ToggleLeftOff01a.png",
            "ui/raw/UI_Flat_ToggleLeftOff01a.png",
            self.panel_rect.left + 340, self.panel_rect.top + 195, 70, 35,
            self.toggle_mute,
        )

   
        self.back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            self.panel_rect.left + 60, self.panel_rect.bottom - 100, 50, 50,
            lambda: scene_manager.change_scene("menu"),
        )

       
        self.exit_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            self.panel_rect.right - 70, self.panel_rect.top + 30, 40, 40,
            lambda: scene_manager.change_scene("menu"),
        )

        pg.mixer.music.set_volume(GameSettings.AUDIO_VOLUME)

   
    def update_knob_position(self):
        """Position knob based on volume"""
        x = self.slider_rect.x + int(GameSettings.AUDIO_VOLUME * (self.slider_rect.width - self.knob_rect.width))
        y = self.slider_rect.y + (self.slider_rect.height - self.knob_rect.height) // 2
        self.knob_rect.topleft = (x, y)

    def update_mute_sprite(self):
        img_path = (
            "ui/raw/UI_Flat_ToggleLeftOn01a.png"
            if self.muted
            else "ui/raw/UI_Flat_ToggleLeftOff01a.png"
        )
        self.mute_button.img_button_default = Sprite(img_path, (self.mute_button.hitbox.w, self.mute_button.hitbox.h))
        self.mute_button.img_button_hover = Sprite(img_path, (self.mute_button.hitbox.w, self.mute_button.hitbox.h))
        self.mute_button.img_button = self.mute_button.img_button_default

   
    def toggle_mute(self):
        self.muted = not self.muted
        GameSettings.MUTED = self.muted

        if sound_manager.current_bgm:
            if self.muted:
                sound_manager.current_bgm.set_volume(0)
            else:
                sound_manager.current_bgm.set_volume(GameSettings.AUDIO_VOLUME)

        self.update_mute_sprite()


    def handle_slider_drag(self):
        mx, my = input_manager.mouse_pos
        mouse_pressed = pg.mouse.get_pressed()[0]

        if self.muted:
            return
        
        if mouse_pressed and (self.knob_rect.collidepoint(mx, my) or self.slider_rect.collidepoint(mx, my)):
            self.dragging = True
        elif not mouse_pressed:
            self.dragging = False

        if self.dragging:
            rel_x = (mx - self.slider_rect.x) / self.slider_rect.width
            rel_x = max(0.0, min(1.0, rel_x))
            GameSettings.AUDIO_VOLUME = rel_x
            self.update_knob_position()

            if sound_manager.current_bgm:
                sound_manager.current_bgm.set_volume(GameSettings.AUDIO_VOLUME)


    @override
    def enter(self):
        sound_manager.play_bgm("RBY 101 Opening (Part 1).ogg")
        if sound_manager.current_bgm:
            if GameSettings.MUTED:
                sound_manager.current_bgm.set_volume(0)
            else:
                sound_manager.current_bgm.set_volume(GameSettings.AUDIO_VOLUME)
        self.update_mute_sprite()
        self.update_knob_position()

    @override
    def update(self, dt: float):
        self.handle_slider_drag()
        self.mute_button.update(dt)
        self.back_button.update(dt)
        self.exit_button.update(dt)

        if input_manager.key_pressed(pg.K_ESCAPE):
            scene_manager.change_scene("menu")

    @override
    def draw(self, screen: pg.Surface):
        self.background.draw(screen)
        screen.blit(self.panel_img, self.panel_rect)

        
        title = self.font_title.render("SETTINGS", True, (0, 0, 0))
        screen.blit(title, (self.panel_rect.left + 160, self.panel_rect.top + 40))

     
        vol_text = self.font_text.render(f"Volume: {int(GameSettings.AUDIO_VOLUME * 100)}%", True, (0, 0, 0))
        screen.blit(vol_text, (self.slider_rect.x, self.slider_rect.y - 40))

       
        pg.draw.rect(screen, (255, 200, 100), self.slider_rect, border_radius=8)
        
        fill_w = int(self.slider_rect.width * GameSettings.AUDIO_VOLUME)
        pg.draw.rect(screen, (220, 220, 220), (self.slider_rect.x, self.slider_rect.y, fill_w, self.slider_rect.height), border_radius=8)
        pg.draw.rect(screen, (255, 255, 255), self.knob_rect)
        pg.draw.rect(screen, (0, 0, 0), self.knob_rect, 2)

       
        mute_text = self.font_text.render(f"Mute: {'On' if self.muted else 'Off'}", True, (0, 0, 0))
        screen.blit(mute_text, (self.panel_rect.left + 100, self.panel_rect.top + 205))
        self.mute_button.draw(screen)

       
        self.back_button.draw(screen)
        self.exit_button.draw(screen)

        esc_text = self.font_text.render("Press ESC to close", True, (0, 0, 0))
        screen.blit(esc_text, (self.back_button.hitbox.right + 15, self.back_button.hitbox.centery - 10))
