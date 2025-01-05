# main_game.py

import os
import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, GRID_ROWS, GRID_COLS, FPS
from background import Background
from inventory import Inventory
from farmer import Farmer
from farm_grid import FarmGrid
from event_handler import EventHandler
from coin import Coin
from coin_animation import CoinAnimation  # 重新啟用 CoinAnimation
from seed import WheatSeed, AppleSeed


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Farm Game")

        # 遊戲物件
        self.background = Background()
        self.farmer = Farmer()
        self.farm_grid = FarmGrid(self.background)

        # 指定字體檔案的路徑
        font_path = "./fonts/zpix.ttf"
        self.font = pygame.font.Font(font_path, 48)  # 金幣大字體
        self.timer_font = pygame.font.Font(font_path, 48)
        self.quantity_font = pygame.font.Font(font_path, 24)

        temp_inventory = Inventory(0, slot_count=5, quantity_font=self.quantity_font)
        inventory_width = temp_inventory.width
        left_inventory_x = 50
        # right_inventory_x = WINDOW_WIDTH - inventory_width - 50  # 被註解掉

        # 建立左側庫存 (seed_inventory)
        self.seed_inventory = Inventory(
            left_inventory_x, slot_count=5, quantity_font=self.quantity_font
        )

        # [註解開始] 暫時關閉右側庫存
        # self.tool_inventory = Inventory(
        #     right_inventory_x, slot_count=5, quantity_font=self.quantity_font
        # )
        # [註解結束]

        # 初始化泥土網格
        self.dirt_grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

        # 初始化事件處理器
        self.event_handler = EventHandler(self)

        # 初始化金幣
        self.coin = Coin(initial_amount=5000)

        # coin_animations 用於 +50 浮動動畫
        self.coin_animations = []

        # [註解開始] 原本每秒增加金幣的測試功能
        # self.coin_timer = pygame.time.get_ticks()
        # self.coin_interval = 1000
        # [註解結束]

        # 初始化遊戲開始時間
        self.start_time = pygame.time.get_ticks()

        # 設置每秒增加小麥種子的計時器（若需要關閉也可註解）
        self.seed_timer = pygame.time.get_ticks()
        self.seed_interval = 1000

        self.clock = pygame.time.Clock()

    def run(self):
        while True:
            # 處理事件
            self.event_handler.handle_events()

            # 更新遊戲狀態
            keys = pygame.key.get_pressed()
            self.farmer.update(keys)

            # [註解開始] 每秒自動增加金幣
            # self.update_coins()
            # [註解結束]

            # 仍保留：每秒增加一顆小麥種子（測試用）
            self.update_seeds()

            # 每幀都檢查是否要讓作物成長（不同泥土有不同速度）
            self.update_plants_growth()

            # (1) 更新所有 coin_animations
            for animation in self.coin_animations[:]:
                animation.update()
                if animation.alpha <= 0:
                    self.coin_animations.remove(animation)

            # (2) 繪製順序開始
            self.background.draw(self.screen)
            self.seed_inventory.draw(self.screen)

            # [註解開始] 暫時關閉右側庫存
            # self.tool_inventory.draw(self.screen)
            # [註解結束]

            for row in self.dirt_grid:
                for dirt in row:
                    if dirt:
                        dirt.draw(self.screen)

            self.farmer.draw(self.screen)

            # 先繪製金幣文字
            self.draw_coins()

            # 繪製計時器
            self.draw_timer()

            # 畫出網格(除錯用)
            self.draw_grid_lines()

            # (3) 確保最後再把動畫畫在最上層
            for animation in self.coin_animations:
                animation.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

    # [註解開始] 原本「每秒增加金幣」的測試功能
    # def update_coins(self):
    #     current_time = pygame.time.get_ticks()
    #     if current_time - self.coin_timer >= self.coin_interval:
    #         self.coin_timer = current_time
    #         self.coin.increase(50)
    #         # 這裡本來也會產生 +50 動畫
    # [註解結束]

    def update_seeds(self):
        """每 1 秒增加一顆小麥種子。"""
        current_time = pygame.time.get_ticks()
        if current_time - self.seed_timer >= self.seed_interval:
            self.seed_timer = current_time
            wheat_seed = WheatSeed()
            self.seed_inventory.add_item(wheat_seed, quantity=1)

    def update_plants_growth(self):
        """
        每幀都檢查所有已種下的植物，如果符合
        『基準成長時間 (2秒) * (1 - growth_speed_bonus)』的條件，
        就讓植物長一階 (stage + 1)。
        """
        current_time = pygame.time.get_ticks()
        base_grow_time = 2000  # 2 秒 = 2000 毫秒

        for row in self.dirt_grid:
            for dirt in row:
                if dirt and dirt.plant and dirt.plant.stage < 5:
                    # 計算此泥土的實際成長間隔
                    grow_interval = base_grow_time * (1 - dirt.growth_speed_bonus)
                    # 判斷是否達到成長間隔
                    if current_time - dirt.last_growth_time >= grow_interval:
                        dirt.plant.grow()
                        dirt.last_growth_time = current_time

    def draw_coins(self):
        coin_text = f"金幣：{self.coin.get_amount()}"
        text_surface = self.font.render(coin_text, True, "#FADE51", "#006666")
        self.screen.blit(text_surface, (10, 10))

    def draw_timer(self):
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        text_surface = self.timer_font.render(time_text, True, "#FFFFFF", "#E1D9B5")
        text_rect = text_surface.get_rect()
        text_x = (WINDOW_WIDTH - text_rect.width) // 2
        text_y = 10
        self.screen.blit(text_surface, (text_x, text_y))

    def draw_grid_lines(self):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = self.background.farm_grid_x + col * self.farm_grid.block_width
                y = self.background.farm_grid_y + row * self.farm_grid.block_height
                pygame.draw.rect(
                    self.screen,
                    (255, 0, 0),
                    (x, y, self.farm_grid.block_width, self.farm_grid.block_height),
                    1,
                )

    # === 建立 coin 動畫物件的便利方法 ===
    def create_coin_animation(self, x, y, text="+50", color="#FF3E3E", duration=2000):
        """
        回傳一個 CoinAnimation 物件，讓呼叫方直接加入 self.coin_animations。
        """
        return CoinAnimation(
            x=x,
            y=y,
            text=text,
            font=self.font,  # 若想小字體可換 self.quantity_font
            color=color,
            duration=duration,
        )


if __name__ == "__main__":
    game = Game()
    game.run()
