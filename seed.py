# seed.py

import pygame


class Seed:
    def __init__(self, name, image_path):
        self.name = name
        self.image_path = image_path
        self.image = pygame.image.load(self.image_path).convert_alpha()
        # 縮放圖片大小，以適應庫存格子的尺寸
        self.image = pygame.transform.scale(self.image, (64, 64))  # 根據實際需求調整尺寸


class WheatSeed(Seed):
    def __init__(self):
        super().__init__(name="小麥種子", image_path="./img/CropSeed1.png")


class AppleSeed(Seed):
    def __init__(self):
        super().__init__(name="蘋果種子", image_path="./img/CropSeed2.png")
