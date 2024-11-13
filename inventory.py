# inventory.py

import pygame


class Inventory:
    def __init__(self, x_position, slot_count, quantity_font):
        # 載入道具欄圖片
        self.inventory_image = pygame.image.load("./img/SeedInv.png").convert_alpha()
        # 縮小道具欄圖片大小
        self.inventory_image = pygame.transform.scale(
            self.inventory_image,
            (
                self.inventory_image.get_width() // 2,
                self.inventory_image.get_height() // 2,
            ),
        )
        # 儲存圖片尺寸
        self.width = self.inventory_image.get_width()
        self.height = self.inventory_image.get_height()
        # 設定道具欄位置
        self.x = x_position
        self.y = 810 // 10

        # 道具欄相關屬性
        self.slot_count = slot_count  # 格子數量
        self.slot_width = self.width // self.slot_count  # 每個格子的寬度
        self.slot_height = self.height  # 格子的高度

        # 物品和數量
        self.items = [None] * self.slot_count  # 每個格子存放的物品
        self.quantities = [0] * self.slot_count  # 每個格子的物品數量

        # 字體，用於顯示數量
        self.quantity_font = quantity_font

        # 載入數字圖片
        self.number_images = []
        for i in range(1, slot_count + 1):
            num_image = pygame.image.load(f"./img/Num{i}.png").convert_alpha()
            num_image = pygame.transform.scale(
                num_image,
                (num_image.get_width() // 2, num_image.get_height() // 2),
            )
            self.number_images.append(num_image)

        # 高亮顏色
        self.highlight_color = (255, 255, 0, 100)  # 黃色，透明度 100

        self.show_numbers = False  # 控制數字圖片的顯示和隱藏
        self.selected_slot = None  # 當前選中的格子（0 到 slot_count - 1），None 表示未選中

    def toggle_numbers(self):
        # 切換數字圖片的顯示狀態
        self.show_numbers = not self.show_numbers
        if not self.show_numbers:
            self.clear_selection()

    def select_slot(self, slot_number):
        # 選擇指定的格子（0 到 slot_count - 1）
        if 0 <= slot_number < self.slot_count:
            self.selected_slot = slot_number

    def clear_selection(self):
        # 清除選擇
        self.selected_slot = None

    def add_item(self, item, quantity=1):
        # 將物品添加到庫存中
        for i in range(self.slot_count):
            if self.items[i] is None:
                # 如果格子是空的，添加物品
                self.items[i] = item
                self.quantities[i] = quantity
                return
            elif self.items[i].name == item.name:
                # 如果格子中已有相同的物品，增加數量
                self.quantities[i] += quantity
                return
        # 如果庫存已滿，無法添加
        print("庫存已滿，無法添加物品！")

    def draw(self, screen):
        # 繪製道具欄
        screen.blit(self.inventory_image, (self.x, self.y))

        # 繪製物品圖片和數量
        for i in range(self.slot_count):
            item = self.items[i]
            if item:
                # 計算物品圖片的位置
                slot_x = self.x + i * self.slot_width
                slot_y = self.y
                # 將物品圖片繪製在格子中間
                item_rect = item.image.get_rect(
                    center=(
                        slot_x + self.slot_width // 2,
                        slot_y + self.slot_height // 2,
                    )
                )
                screen.blit(item.image, item_rect)

                # 在物品圖片的右下角繪製數量
                quantity_text = f"x{self.quantities[i]}"
                quantity_surface = self.quantity_font.render(quantity_text, True, (255, 255, 255))
                quantity_rect = quantity_surface.get_rect(
                    bottomright=(
                        slot_x + self.slot_width - 5,
                        slot_y + self.slot_height - 5,
                    )
                )
                screen.blit(quantity_surface, quantity_rect)

        if self.show_numbers:
            # 在每個格子中間繪製數字圖片
            for i in range(self.slot_count):
                num_image = self.number_images[i]
                # 計算數字圖片的位置，使其在格子中間
                slot_x = self.x + i * self.slot_width
                slot_center_x = slot_x + self.slot_width // 2
                slot_center_y = self.y + self.slot_height
                num_rect = num_image.get_rect(center=(slot_center_x, slot_center_y))
                screen.blit(num_image, num_rect)

            if self.selected_slot is not None:
                # 在選中的格子上繪製高亮效果
                slot_x = self.x + self.selected_slot * self.slot_width
                highlight_rect = pygame.Surface(
                    (self.slot_width, self.slot_height), pygame.SRCALPHA
                )
                highlight_rect.fill(self.highlight_color)
                screen.blit(highlight_rect, (slot_x, self.y))
