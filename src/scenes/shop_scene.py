import pygame as pg
from src.scenes.scene import Scene
from src.utils import GameSettings
from src.interface.components.button import Button


class ShopScene(Scene):
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        self.visible = False

        #font
        self.font_title = pg.font.Font("assets/fonts/Minecraft.ttf", 36)
        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", 22)

        #panel
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        self.panel_img = pg.image.load("assets/images/ui/raw/UI_Flat_Frame03a.png").convert_alpha()
        self.panel_img = pg.transform.smoothscale(self.panel_img, (700, 500))
        self.panel_rect = self.panel_img.get_rect(center=(px, py))

        #exit
        self.close_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            self.panel_rect.right - 60, self.panel_rect.top + 20,
            40, 40,
            self.hide
        )

        #tab
        tab_y = self.panel_rect.top + 40
        self.buy_button = Button(
            "UI/button_buy.png", "UI/button_buy_hover.png",
            self.panel_rect.left + 30, tab_y,
            60,60,
            lambda: self.set_mode("buy")
        )
        self.sell_button = Button(
            "UI/button_sell.png", 
            "UI/button_sell_hover.png",
            self.panel_rect.left + 110,
            tab_y,
            60, 60,
            lambda: self.set_mode("sell")
        )

        self.mode = "buy"

        #scroll
        self.scroll_offset = 0
        self.per_page = 4   
        self.max_scroll = 0


        #buttons
        self.buy_icon = (
            "UI/button_shop.png", 
            "UI/button_shop_hover.png"
        )
        self.sell_icon = (
            "UI/button_shop.png", 
            "UI/button_shop_hover.png"
        )

        self.row_buttons = []

    #show/hide shop
    def show(self):
        self.visible = True
        self.scroll_offset = 0

    def hide(self):
        self.visible = False

    def set_mode(self, mode):
        self.mode = mode
        self.scroll_offset = 0

    
    def get_coin_count(self):
        for it in self.game_manager.bag._items_data:
            if it["name"].lower() == "coins":
                return it["count"]
        return 0

    def add_coins(self, amount):
        for it in self.game_manager.bag._items_data:
            if it["name"].lower() == "coins":
                it["count"] += amount
                return
        self.game_manager.bag._items_data.append({
            "name": "Coins",
            "count": amount,
            "sprite_path": "ingame_ui/coin.png"
        })

    def remove_coins(self, amount):
        for it in self.game_manager.bag._items_data:
            if it["name"].lower() == "coins":
                it["count"] = max(0, it["count"] - amount)
                return


    
    def update(self, dt):
        if not self.visible:
            return

        self.close_button.update(dt)
        self.buy_button.update(dt)
        self.sell_button.update(dt)

        for button in self.row_buttons:
            button.update(dt)

        keys = pg.key.get_pressed()

        #down 1 item
        if keys[pg.K_DOWN]:
            if self.scroll_offset < self.max_scroll:
                self.scroll_offset += 1

        if keys[pg.K_UP]:
            if self.scroll_offset > 0:
                self.scroll_offset -= 1


    #buy
    def buy_item(self, item_name, price, sprite_path):
        if self.get_coin_count() < price:
            return 

        self.remove_coins(price)

      
        for it in self.game_manager.bag._items_data:
            if it["name"] == item_name:
                it["count"] += 1
                return

        self.game_manager.bag._items_data.append({
            "name": item_name,
            "count": 1,
            "sprite_path": sprite_path
        })


    #sell
    def sell_item(self, item_name, price):
        items = self.game_manager.bag._items_data

        for it in items:
            if it["name"] == item_name and it["count"] > 0:
                it["count"] -= 1
                self.add_coins(price)
                return

    def sell_monster(self, index, price):
        monster = self.game_manager.bag._monsters_data
        if 0 < index < len(monster):
            monster.pop(index)
            self.add_coins(price)


    
    def draw(self, screen):
        self.row_buttons.clear()
        if not self.visible:
            return

        # dim background
        dim = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        dim.set_alpha(160)
        dim.fill((0, 0, 0))
        screen.blit(dim, (0, 0))

        #panel
        screen.blit(self.panel_img, self.panel_rect)

        # Close
        self.close_button.draw(screen)

        #money
        coins_text = self.font.render(f"Coins: {self.get_coin_count()}", True, (0, 0, 0))
        screen.blit(coins_text, (self.panel_rect.left + 190, self.panel_rect.top + 65))

        instruction_text = self.font.render("Press the down arrow key to see more!", True, (0, 0, 0))
        screen.blit(instruction_text, (self.panel_rect.left + 190, self.panel_rect.top + 85))
        
        #buy sell button
        self.buy_button.draw(screen)
        self.sell_button.draw(screen)

       
        if self.mode == "buy":
            self.draw_buy_list(screen)
        else:
            self.draw_sell_list(screen)


   
    def draw_buy_list(self, screen):
        items_for_sale = [
            {"name": "Strength Potion", "price": 20, "icon": "ingame_ui/strength_potion.png"},
            {"name": "Defense Potion", "price": 20, "icon": "ingame_ui/defense_potion.png"},
            {"name": "Heal Potion", "price": 50, "icon": "ingame_ui/heal_potion.png"},
            {"name": "Pokeball", "price": 10, "icon": "ingame_ui/ball.png"},
        ]

        start = self.scroll_offset
        end = start + self.per_page
        view = items_for_sale[start:end]

        self.max_scroll = max(0, len(items_for_sale) - self.per_page)

        y = self.panel_rect.top + 140

        for item in view:
            self.draw_buy_row(screen, item, y)
            y += 80

    def draw_buy_row(self, screen, item, y):
        rect = pg.Rect(self.panel_rect.left + 40, y, 500, 60)
        pg.draw.rect(screen, (255, 245, 220), rect)
        pg.draw.rect(screen, (0, 0, 0), rect, 2)

        #icons
        icon = pg.image.load("assets/images/" + item["icon"]).convert_alpha()
        icon = pg.transform.smoothscale(icon, (40, 40))
        screen.blit(icon, (rect.left + 10, rect.top + 10))

        #name
        screen.blit(self.font.render(item["name"], True, (0, 0, 0)),
                    (rect.left + 70, rect.top + 18))

        #buy button
        button = Button(
            self.buy_icon[0], self.buy_icon[1],
            rect.right + 10, rect.top + 10,
            40, 40,
            lambda n=item["name"], p=item["price"], s=item["icon"]:
                self.buy_item(n, p, s)
        )
        self.row_buttons.append(button)
        button.draw(screen)

        #price
        price_text = self.font.render(f"${item['price']}", True, (0, 0, 0))
        screen.blit(price_text, (rect.right + 60, rect.top + 18))


    
    def draw_sell_list(self, screen):
        monster = self.game_manager.bag._monsters_data
        items = self.game_manager.bag._items_data

        combined = []

        #sell monsters
        for i, m in enumerate(monster):
            if i == 0:
                continue
            combined.append(("mon", i, m))

        #items
        for it in items:
            if it["name"].lower() != "coins": 
                combined.append(("item", None, it))

        start = self.scroll_offset
        end = start + self.per_page
        view = combined[start:end]

        self.max_scroll = max(0, len(combined) - self.per_page)

        y = self.panel_rect.top + 140

        for row in view:
            kind, index, data = row
            if kind == "mon":
                self.draw_monster_row(screen, data, index, y)
            else:
                self.draw_item_sell_row(screen, data, y)
            y += 80

    def draw_monster_row(self, screen, mon, index, y):
        price = 30  
        rect = pg.Rect(self.panel_rect.left + 40, y, 500, 60)
        pg.draw.rect(screen, (255, 245, 220), rect)
        pg.draw.rect(screen, (0, 0, 0), rect, 2)

        icon = pg.image.load("assets/images/" + mon["sprite_path"]).convert_alpha()
        icon = pg.transform.smoothscale(icon, (45, 45))
        screen.blit(icon, (rect.left + 10, rect.top + 8))

        name = f"{mon['name']}  Lv.{mon['level']}"
        screen.blit(self.font.render(name, True, (0, 0, 0)),
                    (rect.left + 70, rect.top + 5))

        # HP bar
        hp = mon["hp"]
        max_hp = mon["max_hp"]
        bar = pg.Rect(rect.left + 70, rect.top + 32, 150, 12)
        pg.draw.rect(screen, (0, 0, 0), bar, 2)
        fill = int((hp / max_hp) * (bar.width - 4))
        pg.draw.rect(screen, (0, 255, 0), (bar.left + 2, bar.top + 2, fill, 8))

        #sell button
        button = Button(
            self.sell_icon[0], self.sell_icon[1],
            rect.right + 10, rect.top + 10,
            40, 40,
            lambda idx=index, p=price: self.sell_monster(idx, p)
        )
        self.row_buttons.append(button)

        button.draw(screen)

        #price
        screen.blit(self.font.render(f"${price}", True, (0, 0, 0)),
                    (rect.right + 60, rect.top + 18))

    def draw_item_sell_row(self, screen, it, y):
        price = 5
        rect = pg.Rect(self.panel_rect.left + 40, y, 500, 60)
        pg.draw.rect(screen, (255, 245, 220), rect)
        pg.draw.rect(screen, (0, 0, 0), rect, 2)

        icon = pg.image.load("assets/images/" + it["sprite_path"]).convert_alpha()
        icon = pg.transform.smoothscale(icon, (40, 40))
        screen.blit(icon, (rect.left + 10, rect.top + 10))

        screen.blit(self.font.render(it["name"], True, (0, 0, 0)),
                    (rect.left + 70, rect.top + 18))

        #count
        screen.blit(self.font.render(f"x{it['count']}", True, (0, 0, 0)),
                    (rect.left + 250, rect.top + 18))

        #sell button
        button = Button(
            self.sell_icon[0], self.sell_icon[1],
            rect.right + 10, rect.top + 10,
            40, 40,
            lambda n=it["name"], p=price: self.sell_item(n, p)
        )
        self.row_buttons.append(button)
        button.update(0)
        button.draw(screen)

        price_text = self.font.render(f"${price}", True, (0, 0, 0))
        screen.blit(price_text, (rect.right + 60, rect.top + 18))
