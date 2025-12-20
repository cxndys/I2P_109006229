import pygame as pg
import random
from typing import override
from src.scenes.scene import Scene
from src.sprites import BackgroundSprite, Animation
from src.utils import GameSettings
from src.core.services import scene_manager, input_manager, sound_manager



element_effectiveness = {
    "Fire": {
        "Grass": 1.5,
        "Water": 0.5,
        "Fire": 1.0
    },
    "Grass": {
        "Water": 1.5,
        "Fire": 0.5,
        "Grass": 1.0
    },
    "Water": {
        "Fire": 1.5,
        "Grass": 0.5,
        "Water": 1.0
    }
    
}


monster_list = [
    {"name": "Charizard", "element": "Grass",  "sprite_path": "menu_sprites/menusprite2.png"},
    {"name": "Blastoise", "element": "Grass", "sprite_path": "menu_sprites/menusprite3.png"},
    {"name": "Venusaur",  "element": "Fire", "sprite_path": "menu_sprites/menusprite4.png"},
    {"name": "Gengar",  "element": "Fire",   "sprite_path": "menu_sprites/menusprite5.png"},
    {"name": "Dragonite", "element": "Water", "sprite_path": "menu_sprites/menusprite6.png"},
    {"name": "Tyranitar", "element": "Fire", "sprite_path": "menu_sprites/menusprite7.png"},
    {"name": "Torterra",  "element": "Fire", "sprite_path": "menu_sprites/menusprite8.png"},
    {"name": "Luxray",  "element": "Fire",   "sprite_path": "menu_sprites/menusprite9.png"},
    {"name": "Flygon",  "element":"Water",   "sprite_path": "menu_sprites/menusprite10.png"},
    {"name": "Squirtle",  "element": "Water", "sprite_path": "menu_sprites/menusprite11.png"},
    {"name": "Ampharos", "element": "Water", "sprite_path": "menu_sprites/menusprite12.png"},
    {"name": "Absol", "element": "Water",    "sprite_path": "menu_sprites/menusprite13.png"},
    {"name": "Eevee", "element":"Water",  "sprite_path": "menu_sprites/menusprite14.png"},
    {"name": "Lucario", "element": "Grass",   "sprite_path": "menu_sprites/menusprite15.png"},
    {"name": "Umbreon", "element": "Grass", "sprite_path": "menu_sprites/menusprite16.png"},
]

monster_evolution ={
    "Pikachu":[
    {"sprite_path": "menu_sprites/menusprite1.png"},
    {"sprite_path": "menu_sprites/menusprite1_evol1.png"},
    {"sprite_path": "menu_sprites/menusprite1_evol2.png"}
    ]
}

items_list = {"Heal Potion", "Strength Potion", "Defense Potion"}



class BattleScene(Scene):
    def __init__(self, game_manager, enemy_trainer):
        self.item_buttons = []

        super().__init__()
        self.sub_state = "main" 
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.font_big = pg.font.Font("assets/fonts/Minecraft.ttf", 28)
        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", 20)

        self.game_manager = game_manager
        self.enemy_trainer = enemy_trainer
        

        #intro
        self.intro_stage = 0
        self.message = "Rival challenges you to a battle!"
        self.turn = "player"
        self.enemy_turn_timer = 0
        self.end_timer = 0
        self.message_timer = 0
        self.next_turn = None
        self.evolved = False
        self.battle_over = False

       #player monster
        monster = self.game_manager.bag._monsters_data
        self.player_monster = monster[0].copy()  
        self.player_monster.setdefault("element", "Grass")
        self.player_monster.setdefault("monster_evolution", 0)

        if "sprite_path" not in self.player_monster:
            self.player_monster["sprite_path"] = "menu_sprites/menusprite1.png"
      
        self.player_monster.setdefault("level", 10)
        self.player_monster.setdefault("max_hp", 100)
        self.player_monster.setdefault("hp", self.player_monster["max_hp"])
        

        #enemy monster
        base = random.choice(monster_list)
        max_hp = random.randint(60, 140)
        level = random.randint(5, 30)
        self.enemy_monster = {
            "name": base["name"],
            "sprite_path": base["sprite_path"],
            "element": base["element"],
            "level": level,
            "max_hp": max_hp,
            "hp": max_hp,
        }

        #buttons
        self.bottom_box = pg.Rect(
            0,
            GameSettings.SCREEN_HEIGHT - 180,
            GameSettings.SCREEN_WIDTH,
            180
        )

        bw, bh = 160, 50
        gap = 25
        bx = GameSettings.SCREEN_WIDTH // 2 - (bw * 2 + gap) // 2 - 100
        by = GameSettings.SCREEN_HEIGHT - 110

        self.button_attack = pg.Rect(bx, by, bw, bh)
        self.button_run = pg.Rect(bx + bw + gap, by, bw, bh)
        self.button_item = pg.Rect(bx + bw + gap * 9, by, bw, bh)

        #evolve/catch button
        self.button_evolve = pg.Rect(
            GameSettings.SCREEN_WIDTH // 2 - 180,
            GameSettings.SCREEN_HEIGHT - 110,
            bw,
            bh
        )
        self.button_catch = pg.Rect(
            GameSettings.SCREEN_WIDTH // 2 + 20,
            GameSettings.SCREEN_HEIGHT - 110,
            bw,
            bh
        )

    

    @override
    def enter(self):
        sound_manager.play_bgm("RBY 107 Battle! (Trainer).ogg")
        if sound_manager.current_bgm:
            if getattr(GameSettings, "MUTED", False):
                sound_manager.current_bgm.set_volume(0)
            else:
                sound_manager.current_bgm.set_volume(GameSettings.AUDIO_VOLUME)


    @override
    def update(self, dt: float):
        if self.sub_state == "post_win":
            self.player_input()
            if not self.battle_over:
                return
        
        #battle end
        if self.battle_over:
            self.end_timer -= dt
            if self.end_timer <= 0:
                scene_manager.change_scene("game")
            return

        #intro
        if self.intro_stage == 0:
            if input_manager.key_pressed(pg.K_ESCAPE):
                scene_manager.change_scene("game")
                return

            elif input_manager.key_pressed(pg.K_RETURN):
                self.intro_stage = 1
                self.message = "What will you do?"
            return

        #what will you do?
        if self.intro_stage == 1:
            if input_manager.key_pressed(pg.K_ESCAPE):
                scene_manager.change_scene("game")
                return

            elif input_manager.key_pressed(pg.K_RETURN):
                self.intro_stage = 2 
            return

        #player or enemy turn
        if self.turn == "player":
            self.player_input()
        else:
            self.enemy_turn()

        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0 and self.next_turn:
                self.turn = self.next_turn
                self.next_turn = None
            return


    #player turn
    def player_input(self):
        #evolve or catch?
        if self.sub_state == "post_win":
            mx, my = input_manager.mouse_pos
            click = input_manager.mouse_pressed(1)

            if click and self.button_evolve.collidepoint(mx, my):
                name = self.player_monster["name"]
                stage = self.player_monster.get("monster_evolution", 0)

                if self.evolved:
                    self.message = "You can only evolve once per battle."
                    return

                elif stage < len(monster_evolution[name]) - 1:
                    self.evolve_player_mon()
                    self.message = f"{self.player_monster['name']} evolved!"
                    self.evolved = True
                else:
                    self.message = "Cannot evolve. Already max."

                self.battle_over = True
                self.end_timer = 1
                return

            elif click and self.button_catch.collidepoint(mx, my):
                if self.catch_mon():
                    self.message = "You caught the Monster!"
                else:
                    self.message = "No pokeballs left!"
                self.battle_over = True
                self.end_timer = 1
                return

            return
        

        #use item
        mx, my = input_manager.mouse_pos
        click = input_manager.mouse_pressed(1)

        if self.sub_state == "item_menu":
            if click:
                for item, rect in self.item_buttons:
                    if rect.collidepoint(mx, my):
                        self.use_item(item)
                        return
            return

        # attack
        if click and self.button_attack.collidepoint(mx, my):
            base_damage = 0.6 * self.player_monster["level"] 
            attacker_element = self.player_monster["element"]
            defender_element = self.enemy_monster["element"]

            multiplier = element_effectiveness[attacker_element][defender_element]
            damage = int(base_damage * multiplier)
            if self.player_monster.get("attack_double"):
                damage *= 2
                self.player_monster["attack_double"] = False
            self.enemy_monster["hp"] = max(0, self.enemy_monster["hp"] - damage)

            if self.enemy_monster["hp"] <= 0:
                self.message = "You win! Evolve or catch the monster?"
                self.sub_state = "post_win"
                self.turn = None
                return

            self.turn = "enemy"
            return

        # run
        if click and self.button_run.collidepoint(mx, my):
            self.message = "You ran away!"
            scene_manager.change_scene("game")
            return
        
        #use item
        elif click and self.button_item.collidepoint(mx, my):
            self.sub_state = "item_menu"
            self.message = "Choose an item."
            return


    #enemy turn
    def enemy_turn(self):
        if self.sub_state == "post_win":
            return
        if self.enemy_turn_timer == 0:
            self.message = "Enemy's turn..."
            self.enemy_turn_timer = 0.5
            return

        self.enemy_turn_timer -= 1 / GameSettings.FPS
        if self.enemy_turn_timer > 0:
            return

        base_damage = 0.6 * self.player_monster["level"] 
        attacker_element = self.player_monster["element"]
        defender_element = self.enemy_monster["element"]

        multiplier = element_effectiveness[attacker_element][defender_element]
        damage = int(base_damage * multiplier)
        if self.player_monster.get("half_damage"):
                damage = damage // 2
                self.player_monster["half_damage"] = False

        self.player_monster["hp"] = max(0, self.player_monster["hp"] - damage)
        self.message = f"Enemy attacks! You -{damage} HP."

        if self.player_monster["hp"] <= 0:
            self.message = "You have been defeated. You lose!"
            self.battle_over = True
            self.end_timer = 1
            return

        self.enemy_turn_timer = 0
        self.turn = "player"

    def use_item(self, item):
        name = item["name"]

        if name == "Heal Potion":
            self.player_monster["hp"] = self.player_monster["max_hp"]

        elif name == "Strength Potion":
            self.player_monster["attack_double"] = True
            self.message = "Next attack will be doubled!"

        elif name == "Defense Potion":
            self.player_monster["half_damage"] = True
            self.message = "Defense increased!"

        item["count"] -= 1
        self.sub_state = "main"
        self.message_timer = 1
        self.next_turn = "enemy"

    def pokeball_count(self) -> int:
        for item in self.game_manager.bag._items_data:
            if item["name"].lower == "pokeball":
                return item["count"]
        return
    
    def catch_mon(self) -> bool:
        for item in self.game_manager.bag._items_data:
            if item["name"].lower() == "pokeball":
                if item["count"] <=0:
                    return False
                
                item["count"] -= 1
                caught_mon = self.enemy_monster.copy()
                caught_mon["hp"] = caught_mon["max_hp"]
                self.game_manager.bag._monsters_data.append(caught_mon)
                return True
                
        

    def evolve_player_mon(self):
        name = self.player_monster["name"]

        #change the sprite
        stage = self.player_monster.get("monster_evolution", 0)
        stage += 1
        self.player_monster["monster_evolution"] = stage
        self.player_monster["sprite_path"] = monster_evolution[name][stage]["sprite_path"]

        self.player_monster["level"] += 15
        self.player_monster["max_hp"] += 30
        self.player_monster["hp"] = self.player_monster["max_hp"]

        for i, monster in enumerate(self.game_manager.bag._monsters_data):
            if monster["name"] == name:
                self.game_manager.bag._monsters_data[i] = self.player_monster.copy()
                break

    
    @override
    def draw(self, screen: pg.Surface):
        self.background.draw(screen)

        #monster
        self.draw_monster(
            screen, 
            self.player_monster,
            x=160,
            y=360, 
            flip=True
        )
        self.draw_monster(
            screen, 
            self.enemy_monster,
            x=820, 
            y=180,
            flip=False
        )

        # textbox
        pg.draw.rect(screen, (30, 30, 30), self.bottom_box)

        #message
        message_surface = self.font.render(self.message, True, (255, 255, 255))
        screen.blit(message_surface, (30, self.bottom_box.y + 25))

        
        if self.intro_stage in (0, 1):
            enter_text = self.font.render("Press ENTER to continue", True, (200, 200, 200))
            screen.blit(enter_text, (1010, self.bottom_box.y + 150))

            exit_text = self.font.render("Press ESC to exit", True, (200, 200, 200))
            screen.blit(exit_text, (20, self.bottom_box.y + 150))
            return

        # buttons
        if self.sub_state == "post_win":
            self.draw_button(screen, self.button_evolve, "Evolve")
            self.draw_button(screen, self.button_catch, "Catch")
            return

        if not self.battle_over and self.turn == "player":
            if self.sub_state == "main":
                self.draw_button(screen, self.button_attack, "Fight")
                self.draw_button(screen, self.button_item, "Use Item")
                self.draw_button(screen, self.button_run, "Run")
        
            elif self.sub_state == "item_menu":
                self.draw_item_menu(screen)

   
    def draw_monster(self, screen, mon, x, y, flip=False):
        # sprite
        try:
            path = "assets/images/" + mon["sprite_path"]
            img = pg.image.load(path).convert_alpha()
        except Exception:
            img = pg.Surface((150, 150))
            img.fill((255, 0, 0))

        img = pg.transform.smoothscale(img, (150, 150))
        if flip:
            img = pg.transform.flip(img, True, False)
        screen.blit(img, (x, y))

        # info box
        box = pg.Rect(x, y - 70, 260, 60)
        pg.draw.rect(screen, (245, 245, 245), box)
        pg.draw.rect(screen, (0, 0, 0), box, 2)

        # name + level
        name = self.font.render(f"{mon['name']}  Lv{mon['level']}", True, (0, 0, 0))
        screen.blit(name, (box.x + 10, box.y + 6))

        # hp bar
        ratio = mon["hp"] / mon["max_hp"]
        bar_w = int(180 * ratio)
        pg.draw.rect(screen, (40, 40, 40), (box.x + 10, box.y + 32, 180, 10))
        pg.draw.rect(screen, (110, 220, 110), (box.x + 10, box.y + 32, bar_w, 10))

        # hp numbers
        hp_txt = self.font.render(f"{mon['hp']}/{mon['max_hp']}", True, (0, 0, 0))
        screen.blit(hp_txt, (box.x + 200, box.y + 28))

   
    def draw_button(self, screen, rect, label):
        pg.draw.rect(screen, (240, 240, 240), rect)
        pg.draw.rect(screen, (0, 0, 0), rect, 2)

        txt = self.font.render(label, True, (0, 0, 0))
        screen.blit(txt,(rect.centerx - txt.get_width() // 2,rect.centery - txt.get_height() // 2))

    def draw_item_menu(self, screen):
        self.item_buttons.clear()

        items = self.game_manager.bag._items_data

        bw, bh = 220, 50
        gap = 200
        x = GameSettings.SCREEN_WIDTH // 2 - (bw * 2 + gap) // 2 - 100
        y = GameSettings.SCREEN_HEIGHT - 110

        i = 0
        for item in items:
            if item["name"] not in items_list:
                continue
            elif item["count"] <= 0:
                continue

            rect = pg.Rect(x+ i * (bh + gap), y, bw, bh)
            label = f'{item["name"]} x{item["count"]}'
            self.draw_button(screen, rect, label)
            self.item_buttons.append((item, rect))

            i += 1
        return


    

