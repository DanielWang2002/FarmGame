# background.py
import pygame


class Background:
    def __init__(self):
        # 載入背景圖片
        self.bg_image = pygame.image.load("./img/FarmBG.png")
        # 載入 Farm Grid 圖片
        self.farm_grid = pygame.image.load("./img/FarmGrid.png")
        # 調整圖片位置，微調使其對齊
        self.farm_grid_x = (1440 - self.farm_grid.get_width()) // 2
        self.farm_grid_y = int((810 - self.farm_grid.get_height()) / 1.15)  # 可以微調數值

    def draw(self, screen):
        # 繪製背景和 Farm Grid 圖片
        screen.blit(self.bg_image, (0, 0))
        screen.blit(self.farm_grid, (self.farm_grid_x, self.farm_grid_y))
