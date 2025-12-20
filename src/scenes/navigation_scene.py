import pygame as pg
from src.utils import GameSettings
from src.interface.components.button import Button
from src.scenes.scene import Scene
from src.core.services import scene_manager
from src.utils.findpath import bfs_path
from src.core import GameManager


class NavigationScene(Scene):

    def __init__(self, game_manager):
        super().__init__()

        self.game_manager = game_manager
        self.visible = False

        # fonts
        self.font_title = pg.font.Font("assets/fonts/Minecraft.ttf", 32)
        self.font_small = pg.font.Font("assets/fonts/Minecraft.ttf", 20)
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2

        # panel
        self.panel_img = pg.image.load("assets/images/ui/raw/UI_Flat_Frame03a.png").convert_alpha()
        self.panel_img = pg.transform.smoothscale(self.panel_img, (600, 350))
        self.panel_rect = self.panel_img.get_rect(center=(px, py))

        # exit
        self.exit_button = Button(
            "UI/button_x.png",
            "UI/button_x_hover.png",
            self.panel_rect.right - 55,
            self.panel_rect.top + 20,
            40, 40,
            self.close_overlay
        )

        #destination
        bx = self.panel_rect.left + 100
        by = self.panel_rect.top + 120

        self.start_button = Button(
            "UI/button_play.png",
            "UI/button_play_hover.png",
            bx + 110, by,
            60, 60,
            self.go_to_start
        )

        self.gym_button = Button(
            "UI/button_play.png",
            "UI/button_play_hover.png",
            bx + 210, by,
            60, 60,
            self.go_to_gym
        )

 
    def toggle_visibility(self):
        self.visible = not self.visible

    def close_overlay(self):
        self.visible = False

    #update
    def update(self, dt):
        if not self.visible:
            return

        self.exit_button.update(dt)
        self.start_button.update(dt)
        self.gym_button.update(dt)

    #find shortest path
    def go_to_start(self):
        gm = self.game_manager
        map_obj = gm.current_map

        start = (
            gm.player.position.x // GameSettings.TILE_SIZE,
            gm.player.position.y // GameSettings.TILE_SIZE
        )

        goal = (17, 30)

        path = bfs_path(map_obj, start, goal)
        if path:
            gm.set_navigation_path(path)

        self.close_overlay()

    def go_to_gym(self):
        gm = self.game_manager
        map_obj = gm.current_map

        start = (
            gm.player.position.x // GameSettings.TILE_SIZE,
            gm.player.position.y // GameSettings.TILE_SIZE
        )

        goal = (24, 23)  

        path = bfs_path(map_obj, start, goal)
        if path:
            gm.set_navigation_path(path)

        self.close_overlay()

   
    def draw(self, screen):
        if not self.visible:
            return

        #dim background
        dim = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        dim.set_alpha(180)
        dim.fill((0, 0, 0))
        screen.blit(dim, (0, 0))

        #panel
        screen.blit(self.panel_img, self.panel_rect)

        #title
        title = self.font_title.render("Navigate To", True, (0, 0, 0))
        screen.blit(title, (self.panel_rect.left + 200, self.panel_rect.top + 40))

        #buttons
        self.exit_button.draw(screen)
        self.start_button.draw(screen)
        self.gym_button.draw(screen)

       
        screen.blit(
            self.font_small.render("Start", True, (0, 0, 0)),
            (self.start_button.hitbox.x + 5, self.start_button.hitbox.bottom + 5)
        )

        screen.blit(
            self.font_small.render("Gym", True, (0, 0, 0)),
            (self.gym_button.hitbox.x + 10, self.gym_button.hitbox.bottom + 5)
        )

