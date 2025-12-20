from __future__ import annotations
import pygame
from enum import Enum
from dataclasses import dataclass
from typing import override

from .entity import Entity
from src.sprites import Sprite
from src.core import GameManager
from src.core.services import input_manager, scene_manager
from src.utils import GameSettings, Direction, Position, PositionCamera
from src.scenes.battle_scene import BattleScene


class EnemyTrainerClassification(Enum):
    STATIONARY = "stationary"

@dataclass
class IdleMovement:
    def update(self, enemy: "EnemyTrainer", dt: float) -> None:
        return

class EnemyTrainer(Entity):
    classification: EnemyTrainerClassification
    max_tiles: int | None
    _movement: IdleMovement
    warning_sign: Sprite
    detected: bool
    los_direction: Direction

    @override
    def __init__(
        self,
        x: float,
        y: float,
        game_manager: GameManager,
        classification: EnemyTrainerClassification = EnemyTrainerClassification.STATIONARY,
        max_tiles: int | None = 2,
        facing: Direction | None = None,
    ) -> None:
        super().__init__(x, y, game_manager)
        self.classification = classification
        self.max_tiles = max_tiles
        if classification == EnemyTrainerClassification.STATIONARY:
            self._movement = IdleMovement()
            if facing is None:
                raise ValueError("Idle EnemyTrainer requires a 'facing' Direction at instantiation")
            self._set_direction(facing)
        else:
            raise ValueError("Invalid classification")
        self.warning_sign = Sprite("exclamation.png", (GameSettings.TILE_SIZE // 2, GameSettings.TILE_SIZE // 2))
        self.warning_sign.update_pos(Position(x + GameSettings.TILE_SIZE // 4, y - GameSettings.TILE_SIZE // 2))
        self.detected = False

    @override
    def update(self, dt: float) -> None:
        self._movement.update(self, dt)
        self._has_los_to_player()
        if self.detected and input_manager.key_pressed(pygame.K_SPACE):
            battle = BattleScene(self.game_manager, self)

            scene_manager.register_scene("battle_temp", battle)

    
            scene_manager.change_scene("battle_temp")
            return

        self.animation.update_pos(self.position)

    @override
    def draw(self, screen: pygame.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        if self.detected:
            self.warning_sign.draw(screen, camera)
        if GameSettings.DRAW_HITBOXES:
            los_rect = self._get_los_rect()
            if los_rect is not None:
                pygame.draw.rect(screen, (255, 255, 0), camera.transform_rect(los_rect), 1)

    def _set_direction(self, direction: Direction) -> None:
        self.direction = direction
        if direction == Direction.RIGHT:
            self.animation.switch("right")
        elif direction == Direction.LEFT:
            self.animation.switch("left")
        elif direction == Direction.DOWN:
            self.animation.switch("down")
        else:
            self.animation.switch("up")
        self.los_direction = self.direction

    def _get_los_rect(self) -> pygame.Rect | None:
        '''
        TODO: Create hitbox to detect line of sight of the enemies towards the player
        '''
        tx = int(self.position.x // GameSettings.TILE_SIZE)
        ty = int(self.position.y // GameSettings.TILE_SIZE)
        if self.los_direction == Direction.UP:
            return pygame.Rect(tx, ty - 3, 1, 3)
        elif self.los_direction == Direction.DOWN:
            return pygame.Rect(tx, ty + 1, 1, 3)
        elif self.los_direction == Direction.LEFT:
            return pygame.Rect(tx - 3, ty, 3, 1)
        elif self.los_direction == Direction.RIGHT:
            return pygame.Rect(tx + 1, ty, 1, 1)
        return None

    def _has_los_to_player(self):
        player = self.game_manager.player
        if player is None:
            self.detected = False
            return

    # --- get positions in tile units ---
        tx = int(self.animation.rect.centerx // GameSettings.TILE_SIZE)
        ty = int(self.animation.rect.bottom // GameSettings.TILE_SIZE)

        px = int(player.animation.rect.centerx // GameSettings.TILE_SIZE)
        py = int(player.animation.rect.bottom // GameSettings.TILE_SIZE)

        self.detected = False

    # ------------ UP --------------
        if self.los_direction == Direction.UP:
            if px == tx and py < ty:   # same column AND player above
                self.detected = True
            return

    # ------------ DOWN ------------
        if self.los_direction == Direction.DOWN:
            if px == tx and py > ty:   # same column AND player below
                self.detected = True
            return

    # ------------ LEFT ------------
        if self.los_direction == Direction.LEFT:
            if py == ty and px < tx:   # same row AND player left
                self.detected = True
            return

    # ------------ RIGHT -----------
        if self.los_direction == Direction.RIGHT:
            if py == ty and px > tx:   # same row AND player right
                self.detected = True
            return

       

    @classmethod
    @override
    def from_dict(cls, data: dict, game_manager: GameManager) -> "EnemyTrainer":
        classification = EnemyTrainerClassification(data.get("classification", "stationary"))
        max_tiles = data.get("max_tiles")
        facing_val = data.get("facing")
        facing: Direction | None = None
        if facing_val is not None:
            if isinstance(facing_val, str):
                facing = Direction[facing_val]
            elif isinstance(facing_val, Direction):
                facing = facing_val
        if facing is None and classification == EnemyTrainerClassification.STATIONARY:
            facing = Direction.DOWN
        return cls(
            data["x"] * GameSettings.TILE_SIZE,
            data["y"] * GameSettings.TILE_SIZE,
            game_manager,
            classification,
            max_tiles,
            facing,
        )

    @override
    def to_dict(self) -> dict[str, object]:
        base: dict[str, object] = super().to_dict()
        base["classification"] = self.classification.value
        base["facing"] = self.direction.name
        base["max_tiles"] = self.max_tiles
        return base