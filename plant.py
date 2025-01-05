# plant.py

import pygame


class Plant:
    def __init__(self, image_path, scale=(64, 64)):
        """
        初始化植物時，預設從第 2 階段 (對應 ./img/CropSeed2.png) 開始。
        """
        # 以初始「第 2 階段」作為開始（CropSeed2.png）
        self.stage = 2
        # 定義所有階段對應的圖片路徑（2, 3, 4, 5 階）
        self.growth_stages = [
            "./img/CropSeed2.png",  # 第 2 階段
            "./img/CropSeed3.png",  # 第 3 階段
            "./img/CropSeed4.png",  # 第 4 階段
            "./img/CropSeed5.png",  # 第 5 階段
        ]

        # 載入初始圖片
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, scale)

    def grow(self):
        """
        讓作物成長到下一階段，最高階段到 5（對應 CropSeed5.png）。
        """
        if self.stage < 5:
            self.stage += 1
            # 計算該階段在 self.growth_stages 的索引 (stage 2~5 對應 0~3)
            stage_index = self.stage - 2
            if 0 <= stage_index < len(self.growth_stages):
                new_image_path = self.growth_stages[stage_index]
                self.image = pygame.image.load(new_image_path).convert_alpha()
                # 依實際需求縮放
                self.image = pygame.transform.scale(self.image, (64, 64))
            else:
                # 若超出陣列，代表已經達到最後階段
                self.stage = 5
