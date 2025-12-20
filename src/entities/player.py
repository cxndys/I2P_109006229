from __future__ import annotations
import pygame as pg
from .entity import Entity
from src.core.services import input_manager, scene_manager
from src.utils import Position, PositionCamera, GameSettings, Logger
from src.core import GameManager
import math
from typing import override

class Player(Entity):
    speed: float = 4.0 * GameSettings.TILE_SIZE
    game_manager: GameManager

    def __init__(self, x: float, y: float, game_manager: GameManager) -> None:
        super().__init__(x, y, game_manager)

    @override
    def update(self, dt: float) -> None:
        dis = Position(0, 0)
        
        #[TODO HACKATHON 2]
       # Calculate the distance change, and then normalize the distance
        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            dis.x -= 1
            self.direction = "left"
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            dis.x += 1
            self.direction = "right"
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            dis.y -= 1
            self.direction = "up"
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            dis.y += 1
            self.direction = "down"
        
        diagonal = math.sqrt(dis.x ** 2 + dis.y ** 2)
        if diagonal !=0: 
            dis.x /= diagonal
            dis.y /= diagonal

        dx = dis.x * self.speed * dt
        dy = dis.y * self.speed * dt

        '''
        [TODO HACKATHON 4]
        Check if there is collision, if so try to make the movement smooth
        Hint #1 : use entity.py _snap_to_grid function or create a similar function
        Hint #2 : Beware of glitchy teleportation, you must do
                    1. Update X
                    2. If collide, snap to grid
                    3. Update Y
                    4. If collide, snap to grid
                  instead of update both x, y, then snap to grid
        '''
        padding = 2
        player_rect = pg.Rect(
            self.position.x,
            self.position.y,
            GameSettings.TILE_SIZE - 2 * padding,
            GameSettings.TILE_SIZE - 2 * padding
        )
        def entities(rect: pg.Rect) -> bool:
            scene = scene_manager._current_scene
            for enemy in self.game_manager.current_enemy_trainers:
                enemy_rect = pg.Rect(
                    enemy.position.x,
                    enemy.position.y,
                    GameSettings.TILE_SIZE,
                    GameSettings.TILE_SIZE
                )
                if rect.colliderect(enemy_rect):
                    return True
                
            if hasattr(scene, "shop_npc"):
                for sprite, pos in scene.shop_npc:
                    npc_rect = pg.Rect(
                    pos.x,
                    pos.y,
                    GameSettings.TILE_SIZE,
                    GameSettings.TILE_SIZE
                )
                    if rect.colliderect(npc_rect):
                        return True
                return False
           
          
        player_rect.x += dx
        if self.game_manager.current_map.check_collision(player_rect):
            player_rect.x -= dx
            player_rect.x = self._snap_to_grid(player_rect.x)
        elif entities(player_rect):
            player_rect.x -= dx  


        player_rect.y += dy
        if self.game_manager.current_map.check_collision(player_rect):
            player_rect.y -= dy
            player_rect.y = self._snap_to_grid(player_rect.y)
        elif entities(player_rect):
            player_rect.y -= dy  

        
        self.position.x = player_rect.x
        self.position.y = player_rect.y

        #check teleport
        if not hasattr(self, "_tp_cooldown"):
            self._tp_cooldown = 0
        tp = None
        if self._tp_cooldown > 0:
            self._tp_cooldown -= dt
        else:
            tp = self.game_manager.current_map.check_teleport(self.position)
            
        if tp is not None:
            self.game_manager.last_player_position = self.position.copy()
            dest = tp.destination
            self.game_manager.switch_map(dest)
            self._tp_cooldown = 0.5
            
        #player
        if hasattr(self, "animation") and hasattr(self.animation, "switch"):
            if isinstance(self.direction, str):
                dir_name = self.direction.lower()
            else:
                dir_name = self.direction.name.lower()
            self.animation.switch(dir_name)
            self.animation.update(dt)
            self.animation.update_pos(self.position)
        super().update(dt)

    @override
    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        
    @override
    def to_dict(self) -> dict[str, object]:
        return super().to_dict()
    
    @property
    @override
    def camera(self) -> PositionCamera:
        return PositionCamera(int(self.position.x) - GameSettings.SCREEN_WIDTH // 2, int(self.position.y) - GameSettings.SCREEN_HEIGHT // 2)
            
    @classmethod
    @override
    def from_dict(cls, data: dict[str, object], game_manager: GameManager) -> Player:
        return cls(data["x"] * GameSettings.TILE_SIZE, data["y"] * GameSettings.TILE_SIZE, game_manager)



