import pygame as pg
import json
from src.utils import GameSettings
from src.utils.definition import Monster, Item
from src.interface.components.button import Button



class Bag:
    _monsters_data: list[Monster]
    _items_data: list[Item]

    def __init__(self, monsters_data: list[Monster] | None = None,
                 items_data: list[Item] | None = None):

        self._monsters_data = monsters_data if monsters_data else []
        self._items_data = items_data if items_data else []

        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2

        self.panel_img = pg.image.load("assets/images/ui/raw/UI_Flat_Frame03a.png").convert_alpha()
        self.panel_img = pg.transform.smoothscale(self.panel_img, (700, 500))
        self.panel_rect = self.panel_img.get_rect(center=(px, py))

        self.card_img = pg.image.load("assets/images/ui/raw/UI_Flat_Banner03a.png").convert_alpha()
        self.card_img = pg.transform.smoothscale(self.card_img, (360, 70))

        self.font_title = pg.font.Font("assets/fonts/Minecraft.ttf", 40)
        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", 15)

        
        self.exit_button = Button(
            "UI/button_x.png",
            "UI/button_x_hover.png",
            self.panel_rect.right - 60, self.panel_rect.top + 15,
            40, 40,
            self.close
        )

        #scroll
        self.scroll_offset = 0
        self.per_page = 5

        # Whether bag is currently being shown
        self.visible = False
    
    #save/load monster
    def to_dict(self) -> dict[str, object]:
        return {
            "monsters": list(self._monsters_data),
            "items": list(self._items_data)
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Bag":
        monsters = data.get("monsters") or []
        items = data.get("items") or []
        return cls(monsters, items)

    #open/close bag
    def open(self):
        self.visible = True
        self.scroll_offset = 0

    def close(self):
        self.visible = False

    #update
    def update(self, dt: float):
        if not self.visible:
            return

        self.exit_button.update(dt)

        keys = pg.key.get_pressed()

        if keys[pg.K_DOWN]:
            if self.scroll_offset < max(0, len(self._monsters_data) - self.per_page):
                self.scroll_offset += 1

        if keys[pg.K_UP]:
            if self.scroll_offset > 0:
                self.scroll_offset -= 1

   
    def draw_monster(self, screen, monster, x, y):

        screen.blit(self.card_img, (x, y))


        icon = pg.image.load("assets/images/" + monster["sprite_path"]).convert_alpha()
        icon = pg.transform.smoothscale(icon, (50, 50))
        screen.blit(icon, (x + 20, y))


        name = self.font.render(monster["name"], True, (0, 0, 0))
        level = self.font.render(f"Lv{monster['level']}", True, (0, 0, 0))

        screen.blit(name, (x + 75, y + 10))
        screen.blit(level, (x + 315, y + 25))

        #hp
        hp_ratio = monster["hp"] / monster["max_hp"] if monster["max_hp"] > 0 else 0
        full_w = 220
        bar_h = 10
        bar_x = x + 75
        bar_y = y + 30

        #bg
        pg.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, full_w, bar_h))

        #hp bar 
        fill_w = int(full_w * hp_ratio)
        pg.draw.rect(screen, (110, 220, 110), (bar_x, bar_y, fill_w, bar_h))
        hp_text = self.font.render(f"{monster['hp']}/{monster['max_hp']}", True, (0, 0, 0))
        screen.blit(hp_text, (bar_x, bar_y + bar_h + 4))

    
    def draw_item(self, screen, item, x, y):
        icon = pg.image.load("assets/images/" + item["sprite_path"]).convert_alpha()
        icon = pg.transform.smoothscale(icon, (40, 40))
        screen.blit(icon, (x, y))

        name = self.font.render(item["name"], True, (0, 0, 0))
        cnt = self.font.render(f"x{item['count']}", True, (0, 0, 0))
        screen.blit(name, (x + 60, y + 10))
        screen.blit(cnt, (x + 200, y + 10))

    
    def draw(self, screen: pg.Surface):
        if not self.visible:
            return

        #dim background
        dim = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        dim.set_alpha(160)
        dim.fill((0, 0, 0))
        screen.blit(dim, (0, 0))

        #panel
        screen.blit(self.panel_img, self.panel_rect)

        #title
        title_x = self.panel_rect.left + 30
        title_y = self.panel_rect.top + 25

        title = self.font_title.render("BAG", True, (0, 0, 0))
        screen.blit(title, (title_x, title_y))

        # monster count
        total = len(self._monsters_data)
        count_text = self.font.render(
            f"Monsters: {total}. Press the down arrow key to see more!",
            True, (0, 0, 0)
        )
        screen.blit(count_text, (title_x + 100, title_y + 10))

        # monster list 
        x = self.panel_rect.left + 40
        y = self.panel_rect.top + 70

        visible = self._monsters_data[self.scroll_offset:self.scroll_offset + self.per_page]

        for monster in visible:
            self.draw_monster(screen, monster, x, y)
            y += 80

        # items
        ix = self.panel_rect.left + 420
        iy = self.panel_rect.top + 120

        items_title = self.font.render("Items:", True, (0, 0, 0))
        screen.blit(items_title, (ix, iy - 40))

        for item in self._items_data:
            self.draw_item(screen, item, ix, iy)
            iy += 60

        self.exit_button.draw(screen)




    