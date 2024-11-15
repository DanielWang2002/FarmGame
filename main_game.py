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
from coin_animation import CoinAnimation
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
        self.font = pygame.font.Font(font_path, 48)
        self.timer_font = pygame.font.Font(font_path, 48)
        self.quantity_font = pygame.font.Font(font_path, 24)  # 用於顯示數量

        # 創建庫存實例
        temp_inventory = Inventory(0, slot_count=5, quantity_font=self.quantity_font)
        inventory_width = temp_inventory.width
        left_inventory_x = 50
        right_inventory_x = WINDOW_WIDTH - inventory_width - 50
        self.seed_inventory = Inventory(
            left_inventory_x, slot_count=5, quantity_font=self.quantity_font
        )
        self.tool_inventory = Inventory(
            right_inventory_x, slot_count=5, quantity_font=self.quantity_font
        )

        # 初始化泥土網格
        self.dirt_grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

        # 初始化事件處理器
        self.event_handler = EventHandler(self)

        # 初始化金幣
        self.coin = Coin(initial_amount=5000)

        # 初始化金幣動畫列表
        self.coin_animations = []

        # 設置每秒增加金幣的計時器
        self.coin_timer = pygame.time.get_ticks()
        self.coin_interval = 1000  # 每 1000 毫秒（1 秒）增加一次

        # 初始化遊戲開始時間
        self.start_time = pygame.time.get_ticks()

        # 設置每秒增加小麥種子的計時器
        self.seed_timer = pygame.time.get_ticks()
        self.seed_interval = 1000  # 每 1000 毫秒（1 秒）增加一次

        self.clock = pygame.time.Clock()

    def run(self):
        while True:
            # 處理事件
            self.event_handler.handle_events()

            # 更新遊戲狀態
            keys = pygame.key.get_pressed()
            self.farmer.update(keys)

            # 測試用：更新金幣
            self.update_coins()

            # 測試用：更新種子庫存
            self.update_seeds()

            # 更新金幣動畫
            for animation in self.coin_animations[:]:
                animation.update()
                if animation.alpha <= 0:
                    self.coin_animations.remove(animation)

            # 繪製遊戲場景
            self.background.draw(self.screen)
            self.seed_inventory.draw(self.screen)
            self.tool_inventory.draw(self.screen)

            for row in self.dirt_grid:
                for dirt in row:
                    if dirt:
                        dirt.draw(self.screen)

            self.farmer.draw(self.screen)

            # 繪製金幣和動畫
            self.draw_coins()
            for animation in self.coin_animations:
                animation.draw(self.screen)

            # 繪製遊戲時間
            self.draw_timer()

            # 檢查用：畫出網格邊界
            self.draw_grid_lines()

            pygame.display.flip()
            self.clock.tick(FPS)

    def update_coins(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.coin_timer >= self.coin_interval:
            self.coin_timer = current_time
            self.coin.increase(50)

            # 在金幣位置旁添加一個 '+50' 的動畫
            coin_text_width, _ = self.font.size(f"金幣：{self.coin.get_amount()}")
            animation = CoinAnimation(
                x=10 + coin_text_width + 10,  # 在金幣數字後面一點
                y=10,
                text="+50",
                font=self.font,
                color="#FF3E3E",
                duration=1000,  # 動畫持續 1 秒
            )
            self.coin_animations.append(animation)

    def update_seeds(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.seed_timer >= self.seed_interval:
            self.seed_timer = current_time
            # 添加一個小麥種子到種子庫存
            wheat_seed = WheatSeed()
            self.seed_inventory.add_item(wheat_seed, quantity=1)

    def draw_coins(self):
        coin_text = f"金幣：{self.coin.get_amount()}"
        text_surface = self.font.render(coin_text, True, "#FADE51", "#006666")
        self.screen.blit(text_surface, (10, 10))

    def draw_timer(self):
        # 計算經過的時間（以秒為單位）
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        # 轉換為 mm:ss 格式
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_text = f"{minutes:02d}:{seconds:02d}"
        # 渲染文字
        text_surface = self.timer_font.render(time_text, True, "#FFFFFF", "#E1D9B5")
        # 獲取文字寬度和高度
        text_rect = text_surface.get_rect()
        # 計算文字的位置，使其在螢幕頂部中央
        text_x = (WINDOW_WIDTH - text_rect.width) // 2
        text_y = 10  # 距離頂部 10 像素
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


if __name__ == "__main__":
    game = Game()
    game.run()
