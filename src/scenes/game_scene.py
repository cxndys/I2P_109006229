import pygame as pg

from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.core.services import sound_manager, input_manager
from src.sprites import Sprite
from typing import override
from src.interface.components.button import Button
from src.scenes.setting_scene_in_game import SettingSceneInGame
from src.scenes.navigation_scene import NavigationScene
from src.core.services import scene_manager
from src.scenes.shop_scene import ShopScene
from  src.interface.components.chat_overlay import ChatOverlay


class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite
    
    def __init__(self):
        super().__init__()

        # Load Game Manager
        manager = GameManager.load("saves/game0.json")
        if manager and manager.player:
            default_spawn = manager.current_map.spawn
            manager.player.position.x = default_spawn.x
            manager.player.position.y = default_spawn.y
        if manager is None:
            Logger.error("Failed to load game manager")
            exit(1)
        self.game_manager = manager

        
         # Online Manager
        if GameSettings.IS_ONLINE:
            self.online_manager = OnlineManager()
            self.chat_overlay = ChatOverlay(
                send_callback= self.online_manager.send_chat,
                get_messages= self.online_manager.get_recent_chat   
            )
        else:
            self.online_manager = None
        self.sprite_online = Sprite("ingame_ui/options1.png", (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
        self._chat_bubbles: Dict[int, Tuple[str, str]] = {}
        self._last_chat_id_seen = 0
        

        self.shop_npc = []
        for npc in self.game_manager.current_map.shop_npc:
            sprite = Sprite(npc["sprite"], (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
            pos = Position(npc["x"] * GameSettings.TILE_SIZE,
                   npc["y"] * GameSettings.TILE_SIZE)
            self.shop_npc.append((sprite, pos))
        
        #mini map
        self.minimap_width = 200
        self.minimap_height = 150
        self.minimap_surface = None
        self.minimap_map_name = None
        
        #settings
        self.settings_overlay = SettingSceneInGame(self.game_manager)
        self.show_settings = False
        self.settings_overlay.exit_button.on_click = self.toggle_settings

        #navigation
        self.navigation_overlay = NavigationScene(self.game_manager)
        self.show_navigation = False
        self.navigation_overlay.exit_button.on_click = self.toggle_navigation

        #shop
        self.shop_overlay = ShopScene(self.game_manager)
        self.show_shop = False
        self.shop_overlay.close_button.on_click = self.toggle_shop



        #button
        px,py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 3 // 4

        self.button_setting = Button(
            "UI/button_setting.png",
            "UI/button_setting_hover.png",
            px + 550, py - 520,
            75, 75,
            self.toggle_settings    
        )

        self.button_backpack = Button(
            "UI/button_backpack.png",
            "UI/button_backpack_hover.png",
            px + 450, py - 520,
            75, 75,
            lambda: self.game_manager.bag.open()
        )

        self.button_navigation = Button(
            "UI/button_navigation.png",
            "UI/button_navigation_hover.png",
            px + 350, py - 520,
            75, 75,
            self.toggle_navigation
        )

        

    def toggle_settings(self):
        self.show_settings = not self.show_settings
        self.settings_overlay.visible = self.show_settings

    def toggle_navigation(self):
        self.show_navigation = not self.show_navigation
        self.navigation_overlay.visible = self.show_navigation

    def toggle_shop(self):
        self.show_shop = not self.show_shop
        self.shop_overlay.visible = self.show_shop



    
    @override
    def enter(self):
        sound_manager.play_bgm("RBY 103 Pallet Town.ogg")
        if GameSettings.MUTED and sound_manager.current_bgm:
            sound_manager.current_bgm.set_volume(0)
        if self.online_manager:
            self.online_manager.enter()


    @override
    def exit(self):
        if self.online_manager:
            self.online_manager.exit()


    @override
    def update(self, dt: float):


        #stop game if overlay is on
        if self.game_manager.bag.visible:
            self.game_manager.bag.update(dt)
            return   

   
        if self.show_settings:
            self.settings_overlay.update(dt)
            return
        
    
        if self.navigation_overlay.visible:
            self.navigation_overlay.update(dt)
            return
        
        if self.show_shop:
            self.shop_overlay.update(dt)
            return

        #shop
        if input_manager.key_pressed(pg.K_SPACE):
            px = int(self.game_manager.player.position.x // GameSettings.TILE_SIZE)
            py = int(self.game_manager.player.position.y // GameSettings.TILE_SIZE)

            for sprite, pos in self.shop_npc:
                nx = int(pos.x // GameSettings.TILE_SIZE)
                ny = int(pos.y // GameSettings.TILE_SIZE)

                if abs(px - nx) + abs(py - ny) <= 2:
                    self.toggle_shop()
                    return


        #bush
        if input_manager.key_pressed(pg.K_RETURN) and self.player_near_bush():
            from src.scenes.catch_scene import CatchScene
            catch_scene = CatchScene(self.game_manager)
            scene_manager.register_scene("catch", catch_scene)
            scene_manager.change_scene("catch")
            return
        
        self.button_navigation.update(dt)
        self.button_backpack.update(dt)
        self.button_setting.update(dt)
        
        self.game_manager.try_switch_map()

        if self.game_manager.player:
            self.game_manager.player.update(dt)
   
        #navigation
        if self.game_manager.navigation_path:
            player_tile = (
                int(self.game_manager.player.position.x // GameSettings.TILE_SIZE),
                int(self.game_manager.player.position.y // GameSettings.TILE_SIZE)
            )

            #find closest
            closest_index = None
            shortest_distance = 1_000_000

            for i, (tx, ty) in enumerate(self.game_manager.navigation_path):
                dx = tx - player_tile[0]
                dy = ty - player_tile[1]
                d2 = dx * dx + dy * dy
                if d2 < shortest_distance:
                    shortest_distance = d2
                    closest_index = i

            tile_off = 1.5
            if closest_index is not None and shortest_distance <= tile_off:
                if closest_index > 0:
                    self.game_manager.navigation_path = self.game_manager.navigation_path[closest_index:]

            #turn off navigation if done
            if not self.game_manager.navigation_path:
                self.show_navigation = False

        for enemy in self.game_manager.current_enemy_trainers:
            enemy.update(dt)

        self.game_manager.bag.update(dt)

    """
        #TODO: UPDATE CHAT OVERLAY:

        if self._chat_overlay:
            if input_manager.key_pressed(pg.K_c):
                self._chat_overlay.open()
                self._chat_overlay.update(dt)
        # Update chat bubbles from recent messages

        # This part's for the chatting feature, we've made it for you.
        if self.online_manager:
            try:
                msgs = self.online_manager.get_recent_chat(50)
                max_id = self._last_chat_id_seen
                now = time.monotonic()
                for m in msgs:
                    mid = int(m.get("id", 0))
                    if mid <= self._last_chat_id_seen:
                         continue
                    sender = int(m.get("from", -1))
                    text = str(m.get("text", ""))
                    if sender >= 0 and text:
                        self._chat_bubbles[sender] = (text, now + 5.0)
                    if mid > max_id:
                        max_id = mid
                self._last_chat_id_seen = max_id
            except Exception:
                    pass
       

        if self.online_manager and self.game_manager.player:
            self.online_manager.update(
                self.game_manager.player.position.x,
                self.game_manager.player.position.y,
                self.game_manager.current_map.path_name
            )
   """
    def player_near_bush(self):
        tmx = self.game_manager.current_map.tmxdata
        layer = None
        for name in ("PokemonBush", "Bush", "pokemonbush", "bush"):
            try:
                layer = tmx.get_layer_by_name(name)
                break
            except:
                continue

        if layer is None:
            return False

        px = int(self.game_manager.player.position.x // GameSettings.TILE_SIZE)
        py = int(self.game_manager.player.position.y // GameSettings.TILE_SIZE)

        around = [(0,0),(1,0),(-1,0),(0,1),(0,-1)]

        for dx,dy in around:
            tx = px + dx
            ty = py + dy

        
            try:
                gid = layer.data[ty][tx]
            except:
                continue

            if gid != 0:
                return True

        return False
    
    def minimap(self):
        current_map = self.game_manager.current_map
        tmx = current_map.tmxdata
        map_px_width = tmx.width * GameSettings.TILE_SIZE
        map_py_height = tmx.height * GameSettings.TILE_SIZE

        map_surface = pg.Surface((map_px_width, map_py_height),pg.SRCALPHA)

        current_map.draw(map_surface, PositionCamera(0,0))

        self.minimap_surface = pg.transform.smoothscale(
            map_surface,
            (self.minimap_width,self.minimap_height)
        )

        self.minimap_map_name = current_map.path_name

    def draw_minimap(self,screen):
        current_map = self.game_manager.current_map
        if self.minimap_map_name != current_map.path_name:
            self.minimap()

        screen.blit(self.minimap_surface,(20,20))

        px = self.game_manager.player.position.x
        py = self.game_manager.player.position.y

        tmx = self.game_manager.current_map.tmxdata
        map_px_width = tmx.width * GameSettings.TILE_SIZE
        map_px_height = tmx.height * GameSettings.TILE_SIZE

        scale_x = self.minimap_width / map_px_width
        scale_y = self.minimap_height / map_px_height

        minimap_x = int(px * scale_x)
        minimap_y = int(py * scale_y)

        pg.draw.circle(screen,(255,0,0),(20+ minimap_x, 20 + minimap_y), 3)

        


    @override
    def draw(self, screen: pg.Surface):

     
        
        if self.game_manager.player:
            camera = self.game_manager.player.camera
            map_width = self.game_manager.current_map.tmxdata.width * GameSettings.TILE_SIZE
            map_height = self.game_manager.current_map.tmxdata.height * GameSettings.TILE_SIZE

            camera.x = max(0, min(camera.x, map_width - GameSettings.SCREEN_WIDTH))
            camera.y = max(0, min(camera.y, map_height - GameSettings.SCREEN_HEIGHT))

            self.game_manager.current_map.draw(screen, camera)
            self.game_manager.player.draw(screen, camera)
        else:
            camera = PositionCamera(0, 0)
            self.game_manager.current_map.draw(screen, camera)
     
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)

        for sprite, pos in self.shop_npc:
            x,y = camera.transform_position(pos)
            sprite.update_pos(Position(x,y))
            sprite.draw(screen)


        # -----------------------
        # Online players
        # -----------------------
        if self.online_manager and self.game_manager.player:
            for player in self.online_manager.get_list_players():
                if player["map"] == self.game_manager.current_map.path_name:
                    cam = self.game_manager.player.camera
                    pos = cam.transform_position_as_position(Position(player["x"], player["y"]))
                    self.sprite_online.update_pos(pos)
                    self.sprite_online.draw(screen)

            # try:
            #     self._draw_chat_bubbles(...)
            # except Exception:
            #     pass

      
        self.button_navigation.draw(screen)
        self.button_backpack.draw(screen)
        self.button_setting.draw(screen)

        #navigation path
        if self.game_manager.navigation_path:
            for i in range(len(self.game_manager.navigation_path) - 1):
                x1, y1 = self.game_manager.navigation_path[i]
                x2, y2 = self.game_manager.navigation_path[i + 1]

             
                px = x1 * GameSettings.TILE_SIZE
                py = y1 * GameSettings.TILE_SIZE
                sx, sy = camera.transform_position(Position(px, py))

                
                pg.draw.circle(
                    screen, 
                    (255, 0, 0),
                    (sx + 16, sy + 16),
                    5
                )

              
                nx = x2 * GameSettings.TILE_SIZE
                ny = y2 * GameSettings.TILE_SIZE
                ex, ey = camera.transform_position(Position(nx, ny))

              
                pg.draw.line(
                    screen,
                    (255, 0, 0),
                    (sx + 16, sy + 16),
                    (ex + 16, ey + 16),
                    3
                )

       
        if self.game_manager.bag.visible:
            self.game_manager.bag.draw(screen)
            return

   
        if self.show_settings:
            self.settings_overlay.draw(screen)
            return

     
        if self.navigation_overlay.visible:
            self.navigation_overlay.draw(screen)
            return
        
        self.draw_minimap(screen)

        if self.show_shop:
            self.shop_overlay.draw(screen)
            return
    """""
    def _draw_chat_bubbles(self, screen: pg.Surface, camera: PositionCamera) -> None:
        
        # if not self.online_manager:
        #     return
        # REMOVE EXPIRED BUBBLES
        # now = time.monotonic()
        # expired = [pid for pid, (_, ts) in self._chat_bubbles.items() if ts <= now]
        # for pid in expired:
        #     self._chat_bubbles.____(..., ...)
        # if not self._chat_bubbles:
        #     return

        # DRAW LOCAL PLAYER'S BUBBLE
        # local_pid = self.____
        # if self.game_manager.player and local_pid in self._chat_bubbles:
        #     text, _ = self._chat_bubbles[...]
        #     self._draw_bubble_for_pos(..., ..., ..., ..., ...)

        # DRAW OTHER PLAYERS' BUBBLES
        # for pid, (text, _) in self._chat_bubbles.items():
        #     if pid == local_pid:
        #         continue
        #     pos_xy = self._online_last_pos.____(..., ...)
        #     if not pos_xy:
        #         continue
        #     px, py = pos_xy
        #     self._draw_bubble_for_pos(..., ..., ..., ..., ...)

        pass
    
        DRAWING CHAT BUBBLES:
        - When a player sends a chat message, the message should briefly appear above
        that player's character in the world, similar to speech bubbles in RPGs.
        - Each bubble should last only a few seconds before fading or disappearing.
        - Only players currently visible on the map should show bubbles.

         What you need to think about:
            ------------------------------
            1. **Which players currently have messages?**
            You will have a small structure mapping player IDs to the text they sent
            and the time the bubble should disappear.

            2. **How do you know where to place the bubble?**
            The bubble belongs above the player's *current position in the world*.
            The game already tracks each player’s world-space location.
            Convert that into screen-space and draw the bubble there.

            3. **How should bubbles look?**
            You decide. The visual style is up to you:
            - A rounded rectangle, or a simple box.
            - Optional border.
            - A small triangle pointing toward the character's head.
            - Enough padding around the text so it looks readable.

            4. **How do bubbles disappear?**
            Compare the current time to the stored expiration timestamp.
            Remove any bubbles that have expired.

            5. **In what order should bubbles be drawn?**
            Draw them *after* world objects but *before* UI overlays.

        Reminder:
        - For the local player, you can use the self.game_manager.player.position to get the player's position
        - For other players, maybe you can find some way to store other player's last position?
        - For each player with a message, maybe you can call a helper to actually draw a single bubble?
        

def _draw_chat_bubble_for_pos(self, screen: pg.Surface, camera: PositionCamera, world_pos: Position, text: str, font: pg.font.Font):
    pass
    
    Steps:
        ------------------
        1. Convert a player’s world position into a location on the screen.
        (Use the camera system provided by the game engine.)

        2. Decide where "above the player" is.
        Typically a little above the sprite’s head.

        3. Measure the rendered text to determine bubble size.
        Add padding around the text.
"""

    

