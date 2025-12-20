import pygame as pg
from src.scenes.scene import Scene
from src.utils import GameSettings
from src.core.services import scene_manager, input_manager, sound_manager
from src.sprites import BackgroundSprite
import random

monster_list = [
    {"name": "Pikachu",   "sprite_path": "menu_sprites/menusprite1.png"},
    {"name": "Charizard", "sprite_path": "menu_sprites/menusprite2.png"},
    {"name": "Blastoise", "sprite_path": "menu_sprites/menusprite3.png"},
    {"name": "Venusaur",  "sprite_path": "menu_sprites/menusprite4.png"},
    {"name": "Gengar",    "sprite_path": "menu_sprites/menusprite5.png"},
    {"name": "Dragonite", "sprite_path": "menu_sprites/menusprite6.png"},
    {"name": "Tyranitar",   "sprite_path": "menu_sprites/menusprite7.png"},
    {"name": "Torterra", "sprite_path": "menu_sprites/menusprite8.png"},
    {"name": "Luxray", "sprite_path": "menu_sprites/menusprite9.png"},
    {"name": "Flygon",  "sprite_path": "menu_sprites/menusprite10.png"},
    {"name": "Squirtle",    "sprite_path": "menu_sprites/menusprite11.png"},
    {"name": "Ampharos", "sprite_path": "menu_sprites/menusprite12.png"},
    {"name": "Absol", "sprite_path": "menu_sprites/menusprite13.png"},
    {"name": "Eevee",  "sprite_path": "menu_sprites/menusprite14.png"},
    {"name": "Lucario",    "sprite_path": "menu_sprites/menusprite15.png"},
    {"name": "Umbreon", "sprite_path": "menu_sprites/menusprite16.png"}
]


class CatchScene(Scene):
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager

        self.background = BackgroundSprite("backgrounds/background1.png")
        self.font_big = pg.font.Font("assets/fonts/Minecraft.ttf", 32)
        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", 20)

        

        base = random.choice(monster_list)
        self.mon = {
            "name": base["name"],
            "sprite_path": base["sprite_path"],
            "level": random.randint(3, 20),
            "hp": random.randint(30, 120),
            "max_hp": random.randint(40, 140),
        }

        self.message = f"A wild {self.mon['name']} appeared!"
        self.catch_chance = random.randint(45, 90)

  
        self.intro_stage = 0     
        self.bottom_box = pg.Rect(
            0, GameSettings.SCREEN_HEIGHT - 180,
            GameSettings.SCREEN_WIDTH, 180
        )

        #button
        bw, bh = 160, 50
        gap = 25
        bx = GameSettings.SCREEN_WIDTH // 2 - (bw * 2 + gap) // 2
        by = GameSettings.SCREEN_HEIGHT - 110

        self.button_catch = pg.Rect(bx, by, bw, bh)
        self.button_run = pg.Rect(bx + bw + gap, by, bw, bh)

  
        self.catch_result_stage = None
        self.end_timer = 0

    
    def enter(self):
        sound_manager.play_bgm("RBY 107 Battle! (Trainer).ogg")
        if sound_manager.current_bgm:
            if getattr(GameSettings, "MUTED", False):
                sound_manager.current_bgm.set_volume(0)
            else:
                sound_manager.current_bgm.set_volume(GameSettings.AUDIO_VOLUME)

    def update(self, dt):
  
        if self.catch_result_stage is not None:
            self.end_timer -= dt
            if self.end_timer <= 0:
                scene_manager.change_scene("game")
            return

    
        if self.intro_stage == 0:
            if input_manager.key_pressed(pg.K_ESCAPE):
                scene_manager.change_scene("game")
                return
            if input_manager.key_pressed(pg.K_RETURN):
                self.intro_stage = 1
                self.message = "What will you do?"
            return

        if self.intro_stage == 1:
            if input_manager.key_pressed(pg.K_ESCAPE):
                scene_manager.change_scene("game")
                return
            if input_manager.key_pressed(pg.K_RETURN):
                self.intro_stage = 2
            return

     
        if self.intro_stage == 2:
            mx, my = input_manager.mouse_pos
            click = input_manager.mouse_pressed(1)

            # Catch
            if click and self.button_catch.collidepoint(mx, my):
                if not self.use_pokeball():
                    self.message = "Not enough pokeballs!"
                    self.end_timer = 1
                    scene_manager.change_scene("game")
                    return 
                
                self.attempt_catch()

            # Run
            if click and self.button_run.collidepoint(mx, my):
                self.message = "You ran away!"
                self.catch_result_stage = "run"
                self.end_timer = 1
                return


    def pokeball_count(self) -> int:
        for item in self.game_manager.bag._items_data:
            if item["name"].lower == "pokeball":
                return item["count"]
        return
    
    def use_pokeball(self) -> bool:
        for item in self.game_manager.bag._items_data:
            if item["name"].lower() == "pokeball":
                if item["count"] > 0:
                    item["count"] -= 1
                    return True
                else:
                    return False
    
    def attempt_catch(self):
        roll = random.randint(1, 100)

        if roll <= self.catch_chance:
            self.message = f"You caught {self.mon['name']}!"
            self.game_manager.bag._monsters_data.append(self.mon)
        else:
            self.message = f"{self.mon['name']} escaped!"

        self.catch_result_stage = "done"
        self.end_timer = 1

    def draw(self, screen):
        self.background.draw(screen)
        self.draw_monster(screen)

        pg.draw.rect(screen, (30, 30, 30), self.bottom_box)

        msg = self.font.render(self.message, True, (255, 255, 255))
        screen.blit(msg, (30, self.bottom_box.y + 25))
        
        if self.catch_result_stage is not None:
            return    

        if self.intro_stage in (0, 1):
            enter = self.font.render("Press ENTER to continue", True, (200, 200, 200))
            screen.blit(enter, (1020, self.bottom_box.y + 150))

            exit_t = self.font.render("Press ESC to exit", True, (200, 200, 200))
            screen.blit(exit_t, (20, self.bottom_box.y + 150))
            return

       
        self.draw_button(screen, self.button_catch, "Catch")
        self.draw_button(screen, self.button_run, "Run")


    def draw_monster(self, screen):
        try:
            path = "assets/images/" + self.mon["sprite_path"]
            img = pg.image.load(path).convert_alpha()
        except:
            img = pg.Surface((150, 150))
            img.fill((255, 0, 0))

        img = pg.transform.smoothscale(img, (180, 180))
        screen.blit(img, (700, 200))

    
    def draw_button(self, screen, rect, label):
        pg.draw.rect(screen, (240, 240, 240), rect)
        pg.draw.rect(screen, (0, 0, 0), rect, 2)

        txt = self.font.render(label, True, (0, 0, 0))
        screen.blit(
            txt,
            (rect.centerx - txt.get_width() // 2,
             rect.centery - txt.get_height() // 2)
        )
