import pygame as pg
from src.utils import GameSettings, PositionCamera
from src.sprites import Sprite
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import sound_manager, input_manager, scene_manager
from src.core import GameManager



class SettingSceneInGame(Scene):

    def __init__(self,game_manager):
        super().__init__()

        self.game_manager = game_manager
        self.visible = False
        self.font_title = pg.font.Font("assets/fonts/Minecraft.ttf", 38)
        self.font_text = pg.font.Font("assets/fonts/Minecraft.ttf", 20)

        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2

       
        self.panel_img = pg.image.load("assets/images/ui/raw/UI_Flat_Frame03a.png").convert_alpha()
        self.panel_img = pg.transform.smoothscale(self.panel_img, (550, 450))
        self.panel_rect = self.panel_img.get_rect(center=(px, py))

        
        self.slider_rect = pg.Rect(self.panel_rect.left + 100, self.panel_rect.top + 140, 350, 16)
        self.knob_rect = pg.Rect(0, 0, 20, 28)
        self.dragging = False

        self.knob_position()

    
        self.muted = GameSettings.MUTED
        

        self.mute_button = Button(
            "ui/raw/UI_Flat_ToggleLeftOff01a.png",
            "ui/raw/UI_Flat_ToggleLeftOff01a.png",
            self.panel_rect.left + 340, self.panel_rect.top + 200,
            70, 35,
            self.toggle_mute
        )

        
        self.save_button = Button(
            "UI/button_save.png",
            "UI/button_save_hover.png",
            self.panel_rect.left + 80, self.panel_rect.bottom - 110,
            60, 60,
            self.save_game
        )

        
        self.load_button = Button(
            "UI/button_load.png",
            "UI/button_load_hover.png",
            self.panel_rect.left + 160, self.panel_rect.bottom - 110,
            60, 60,
            self.load_game
        )

     
        self.exit_button = Button(
            "UI/button_x.png",
            "UI/button_x_hover.png",
            self.panel_rect.right - 70,
            self.panel_rect.top + 30,
            40, 40,
            self.toggle_visibility
        )

        self.update_mute_sprite()

    def load_game(self):

        if getattr(self, "_loading", False):
            return
        self._loading = True


        self.toggle_visibility()

        new_gm = GameManager.load("saves/game0.json")
        if new_gm is None:
            self._loading = False
            return


        game_scene = scene_manager._current_scene


        game_scene.game_manager = new_gm
        self.game_manager = new_gm

        if new_gm.player:
            new_gm.player.game_manager = new_gm

        for trainers in new_gm.enemy_trainers.values():
            for t in trainers:
                t.game_manager = new_gm

        self._loading = False
        self.toggle_visibility()



    
    def save_game(self):
        self.game_manager.save("saves/game0.json")
    
   
    def toggle_visibility(self):
        self.visible = not self.visible
        self.knob_position()


    def knob_position(self):
        x = self.slider_rect.x + int(GameSettings.AUDIO_VOLUME * (self.slider_rect.width - self.knob_rect.width))
        y = self.slider_rect.y - 6
        self.knob_rect.topleft = (x, y)

    def drag(self):
        if self.muted or not self.visible:
            return
        
        mx, my = input_manager.mouse_pos
        mouse_pressed = pg.mouse.get_pressed()[0]

        if mouse_pressed and (self.knob_rect.collidepoint(mx, my) or self.slider_rect.collidepoint(mx, my)):
            self.dragging = True
        elif not mouse_pressed:
            self.dragging = False

        if self.dragging:
            rel = (mx - self.slider_rect.x) / self.slider_rect.width
            rel = max(0.0, min(1.0, rel))
            GameSettings.AUDIO_VOLUME = rel
            self.knob_position()

            if sound_manager.current_bgm and not self.muted:
                sound_manager.current_bgm.set_volume(GameSettings.AUDIO_VOLUME)



   
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



    def update(self, dt):
        if not self.visible:
            return

        self.drag()

        self.mute_button.update(dt)
        self.exit_button.update(dt)
        self.save_button.update(dt)
        self.load_button.update(dt)


 
    def draw(self, screen):
        if not self.visible:
            return

        # dim background
        bg = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        bg.set_alpha(180)
        bg.fill((0, 0, 0))
        screen.blit(bg, (0, 0))

        # panel
        screen.blit(self.panel_img, self.panel_rect)

        #title
        title = self.font_title.render("SETTINGS", True, (0, 0, 0))
        screen.blit(title, (self.panel_rect.left + 160, self.panel_rect.top + 40))

        #volume text
        txt = self.font_text.render(f"Volume: {int(GameSettings.AUDIO_VOLUME * 100)}%", True, (0, 0, 0))
        screen.blit(txt, (self.slider_rect.x, self.slider_rect.y - 45))

        #slider
        pg.draw.rect(screen, (255, 200, 100), self.slider_rect, border_radius=8)

        fill_w = int(self.slider_rect.width * GameSettings.AUDIO_VOLUME)
        pg.draw.rect(screen, (255, 255, 255),
                     (self.slider_rect.x, self.slider_rect.y, fill_w, self.slider_rect.height),
                     border_radius=8)

        #slider knob
        pg.draw.rect(screen, (255, 255, 255), self.knob_rect)
        pg.draw.rect(screen, (0, 0, 0), self.knob_rect, 2)

        mute_text = self.font_text.render(f"Mute: {'On' if self.muted else 'Off'}", True, (0, 0, 0))
        screen.blit(mute_text, (self.panel_rect.left + 100, self.panel_rect.top + 215))
        self.mute_button.draw(screen)

        
        self.exit_button.draw(screen)
        self.save_button.draw(screen)
        self.load_button.draw(screen)
