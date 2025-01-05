# event_handler.py

import pygame
import sys
from dirt import Dirt
from settings import DIRT_LEVELS
from plant import Plant  # 新增這一行
from seed import WheatSeed  # 確保已導入 Seed 類別


class EventHandler:
    def __init__(self, game):
        self.game = game  # 傳入整個遊戲對象，以便訪問其他組件

    def handle_events(self):
        farmer = self.game.farmer
        farm_grid = self.game.farm_grid
        dirt_grid = self.game.dirt_grid
        background = self.game.background
        seed_inventory = self.game.seed_inventory
        # [註解開始] right_inventory (tool_inventory) 暫時註解掉
        # tool_inventory = self.game.tool_inventory
        # [註解結束]
        coin = self.game.coin  # 獲取金幣對象

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    # 處理按下 'q' 鍵的事件
                    farmer_center_x = farmer.x + farmer.image_width // 2
                    farmer_bottom_y = farmer.y + farmer.image_height
                    grid_position = farm_grid.get_grid_position(farmer_center_x, farmer_bottom_y)
                    if grid_position:
                        grid_x, grid_y = grid_position
                        dirt = dirt_grid[grid_y][grid_x]
                        if dirt is None:
                            # 放置新的泥土，成本為50金幣
                            cost = 50
                            if coin.get_amount() >= cost:
                                dirt = Dirt(
                                    grid_x=grid_x,
                                    grid_y=grid_y,
                                    farm_grid_x=background.farm_grid_x,
                                    farm_grid_y=background.farm_grid_y,
                                    block_width=farm_grid.block_width,
                                    block_height=farm_grid.block_height,
                                    level=0,
                                )
                                dirt_grid[grid_y][grid_x] = dirt
                                coin.decrease(cost)
                            else:
                                print("金幣不足，無法放置泥土！")
                        else:
                            # 嘗試升級泥土
                            if dirt.level < len(DIRT_LEVELS) - 1:
                                upgrade_cost = DIRT_LEVELS[dirt.level]["upgrade_cost"]
                                if coin.get_amount() >= upgrade_cost:
                                    coin.decrease(upgrade_cost)
                                    dirt.upgrade()
                                else:
                                    print("金幣不足，無法升級泥土！")
                            else:
                                print("泥土已達最高等級！")

                elif event.key == pygame.K_w:
                    # 處理按下 'w' 鍵的事件，切換種子庫存的數字顯示狀態
                    seed_inventory.toggle_numbers()
                    if seed_inventory.show_numbers:
                        # [註解開始] tool_inventory 相關
                        # tool_inventory.show_numbers = False
                        # tool_inventory.clear_selection()
                        # [註解結束]
                        pass
                    else:
                        seed_inventory.clear_selection()

                # [註解開始] 按下 'e' 切換道具庫存 (tool_inventory) 的功能，暫時註解
                # elif event.key == pygame.K_e:
                #     tool_inventory.toggle_numbers()
                #     if tool_inventory.show_numbers:
                #         seed_inventory.show_numbers = False
                #         seed_inventory.clear_selection()
                #     else:
                #         tool_inventory.clear_selection()
                # [註解結束]

                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                    # 處理數字鍵 '1' 到 '5' 的按下事件
                    slot_number = int(event.unicode) - 1  # 將 '1'-'5' 轉換為 0-4
                    if seed_inventory.show_numbers:
                        if 0 <= slot_number < seed_inventory.slot_count:
                            item = seed_inventory.items[slot_number]
                            if item and seed_inventory.quantities[slot_number] > 0:
                                # 找到農夫所在的泥土位置
                                farmer_center_x = farmer.x + farmer.image_width // 2
                                farmer_bottom_y = farmer.y + farmer.image_height
                                grid_position = farm_grid.get_grid_position(
                                    farmer_center_x, farmer_bottom_y
                                )
                                if grid_position:
                                    grid_x, grid_y = grid_position
                                    dirt = dirt_grid[grid_y][grid_x]
                                    if dirt:
                                        if dirt.plant is None:
                                            # 種植植物
                                            plant_image_path = "./img/CropSeed2.png"
                                            plant = Plant(
                                                image_path=plant_image_path, scale=(64, 64)
                                            )
                                            dirt.plant_seed(plant)
                                            # 庫存減1
                                            seed_inventory.quantities[slot_number] -= 1
                                            if seed_inventory.quantities[slot_number] == 0:
                                                seed_inventory.items[slot_number] = None
                                        else:
                                            print("這塊泥土已經有植物了！")
                                    else:
                                        print("這塊泥土尚未被初始化！")

                elif event.key == pygame.K_SPACE:
                    # 收穫植物的功能：若植物已到第 5 階，可收穫並獲得 50 金幣
                    farmer_center_x = farmer.x + farmer.image_width // 2
                    farmer_bottom_y = farmer.y + farmer.image_height
                    grid_position = farm_grid.get_grid_position(farmer_center_x, farmer_bottom_y)
                    if grid_position:
                        grid_x, grid_y = grid_position
                        dirt = dirt_grid[grid_y][grid_x]
                        if dirt and dirt.plant:
                            # 若植物已經是第 5 階段，則可以收穫
                            if dirt.plant.stage == 5:
                                coin.increase(50)
                                print("收穫成功，獲得 50 金幣！")
                                # 收穫後移除植物
                                dirt.plant = None

                                # === 新增動畫邏輯 ===
                                coin_text = f"金幣：{coin.get_amount()}"
                                coin_text_width, _ = self.game.font.size(coin_text)

                                # x 座標略靠右（在金幣數字後面 10px）
                                anim_x = 10 + coin_text_width + 10
                                anim_y = 10  # 與金幣顯示同高度

                                animation = self.game.create_coin_animation(
                                    x=anim_x,
                                    y=anim_y,
                                    text="+50",
                                    color="#FF3E3E",
                                    duration=2000,  # 可改 2000 或更久，以免太快消失
                                )
                                self.game.coin_animations.append(animation)
                                # === 動畫邏輯結束 ===

                            else:
                                print("此植物尚未成熟，無法收穫！")
