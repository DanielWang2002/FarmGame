# dirt.py

import pygame
from settings import DIRT_LEVELS
from plant import Plant  # 新增這一行


class Dirt:
    def __init__(
        self,
        grid_x,
        grid_y,
        farm_grid_x,
        farm_grid_y,
        block_width,
        block_height,
        level=0,
    ):
        # 初始化泥土屬性
        self.level = level  # 初始等級為 0（Normal）
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.farm_grid_x = farm_grid_x
        self.farm_grid_y = farm_grid_y
        self.block_width = block_width
        self.block_height = block_height

        # 載入圖片和計算位置
        self.load_image()
        self.calculate_position()

        # 成長速度加成（對應 settings.py 裏 DIRT_LEVELS[self.level]["growth_speed_bonus"]）
        self.growth_speed_bonus = DIRT_LEVELS[self.level]["growth_speed_bonus"]

        # 初始化植物
        self.plant = None  # 初始沒有植物

        # 新增：紀錄最後一次成長時間（毫秒）
        self.last_growth_time = 0

    def load_image(self):
        # 根據等級載入對應的圖片
        image_path = DIRT_LEVELS[self.level]["image"]
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (170, 170))

    def calculate_position(self):
        # 計算泥土圖片的繪製位置，使其在格子中置中
        x = self.farm_grid_x + self.grid_x * self.block_width
        y = self.farm_grid_y + self.grid_y * self.block_height
        # 計算置中偏移
        offset_x = (self.block_width - self.image.get_width()) // 2
        offset_y = (self.block_height - self.image.get_height()) // 2
        self.position = (x + offset_x, y + offset_y)

    def upgrade(self):
        # 升級泥土等級
        if self.level < len(DIRT_LEVELS) - 1:
            self.level += 1
            self.load_image()
            self.growth_speed_bonus = DIRT_LEVELS[self.level]["growth_speed_bonus"]
            print(f"泥土升級到 {DIRT_LEVELS[self.level]['name']} 等級！")
        else:
            print("泥土已達最高等級，無法升級！")

    def plant_seed(self, plant):
        if self.plant is None:
            self.plant = plant
            print(f"種下了 {plant.__class__.__name__}！")
            # 初始化 last_growth_time，在第一次種下時設定
            self.last_growth_time = pygame.time.get_ticks()
        else:
            print("這塊泥土已經有植物了！")

    def draw(self, screen):
        # 將泥土圖片繪製在計算好的位置
        screen.blit(self.image, self.position)
        # 如果有植物，繪製植物圖片
        if self.plant:
            plant_x = self.position[0] + (self.block_width - self.plant.image.get_width()) // 2 - 10
            plant_y = (
                self.position[1] + (self.block_height - self.plant.image.get_height()) // 2 - 10
            )
            screen.blit(self.plant.image, (plant_x, plant_y))
