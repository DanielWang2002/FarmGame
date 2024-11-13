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
        tool_inventory = self.game.tool_inventory
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
                        grid_x, grid_y = grid_position[0], grid_position[1]
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
                        tool_inventory.show_numbers = False
                        tool_inventory.clear_selection()
                    else:
                        seed_inventory.clear_selection()
                elif event.key == pygame.K_e:
                    # 處理按下 'e' 鍵的事件，切換道具庫存的數字顯示狀態
                    tool_inventory.toggle_numbers()
                    if tool_inventory.show_numbers:
                        seed_inventory.show_numbers = False
                        seed_inventory.clear_selection()
                    else:
                        tool_inventory.clear_selection()
                elif event.key in (
                    pygame.K_1,
                    pygame.K_2,
                    pygame.K_3,
                    pygame.K_4,
                    pygame.K_5,
                ):
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
                                    grid_x, grid_y = grid_position[0], grid_position[1]
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
                    elif tool_inventory.show_numbers:
                        # 處理道具庫存的選擇（暫時不處理）
                        tool_inventory.select_slot(slot_number)
