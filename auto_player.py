# auto_player.py

import random
import datetime  # 新增

import pygame
import pandas as pd  # 新增
from pathlib import Path  # 新增

from dirt import Dirt
from main_game import Game
from settings import GRID_ROWS, GRID_COLS, DIRT_LEVELS
from plant import Plant


class AutoGame(Game):
    """
    自動化代理類別，繼承自 Game，直接控制農夫移動並執行動作。
    """

    def __init__(self):
        super().__init__()

        # 總遊戲時間（毫秒，1 分鐘 = 60000 毫秒）
        self.total_time = 60000
        self.start_time = pygame.time.get_ticks()

        # 設定 FPS
        self.FPS = 60

        # 下一次執行隨機動作的時間點（毫秒）
        self.next_action_time = self.start_time + 2000  # 2 秒後首次動作

        # 初始化數據收集結構
        self.game_data = []  # 用於儲存每秒的遊戲狀態
        self.last_record_second = 0  # 上一次記錄的秒數

        # 紀錄遊戲開始的實際時間，用於命名檔案
        self.game_start_datetime = datetime.datetime.now()
        self.csv_filename = f"log/game_{self.game_start_datetime.strftime('%Y%m%d_%H%M%S')}.csv"

        # 確認是否有log資料夾，若無則建立
        Path("log").mkdir(exist_ok=True)

    def run(self):
        """
        覆寫 Game.run()，加入自動化動作流程和數據收集。
        """
        while True:
            # 1. 檢查是否超過總遊戲時間
            current_ticks = pygame.time.get_ticks()
            elapsed = current_ticks - self.start_time
            if elapsed > self.total_time + 1000:
                final_coin = self.coin.get_amount()
                print(f"Time's up! Final coin count = {final_coin}")

                # 在遊戲結束前儲存數據
                self.save_game_data()

                pygame.quit()
                return

            # 2. 檢查是否需要執行下一次動作
            if current_ticks >= self.next_action_time:
                self.do_random_action()
                # 設定下一次動作的時間點（隨機 2~5 秒後）
                self.next_action_time = current_ticks + random.randint(100, 500)

            # 3. 處理事件
            self.event_handler.handle_events()

            # 4. 更新遊戲狀態
            keys = pygame.key.get_pressed()
            self.farmer.update(keys)

            # 5. 更新種子與作物成長
            self.update_seeds()
            self.update_plants_growth()

            # 6. 更新所有金幣動畫
            for animation in self.coin_animations[:]:
                animation.update()
                if animation.alpha <= 0:
                    self.coin_animations.remove(animation)

            # 7. 繪製畫面
            self.background.draw(self.screen)
            self.seed_inventory.draw(self.screen)

            for row in self.dirt_grid:
                for dirt in row:
                    if dirt:
                        dirt.draw(self.screen)

            self.farmer.draw(self.screen)
            self.draw_coins()
            self.draw_timer()
            self.draw_grid_lines()

            for animation in self.coin_animations:
                animation.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(self.FPS)

            # 8. 每秒記錄一次遊戲狀態
            self.record_game_state(current_ticks)

    def do_random_action(self):
        """
        執行一次隨機動作：先嘗試收穫，若無則隨機放土與種植。
        """
        # 先嘗試收穫
        harvested = self.try_harvest()
        if not harvested:
            # 若無可收穫的作物，則隨機放土與種植
            self.place_soil_and_plant()

    def try_harvest(self):
        """
        檢查所有農地，若有植物已到第 5 階段，則移動農夫至該位置並收穫。
        回傳是否有成功收穫。
        """
        # 收集所有成熟的作物位置
        candidates = []
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                dirt = self.dirt_grid[r][c]
                if dirt and dirt.plant and dirt.plant.stage == 5:
                    candidates.append((r, c))
        if not candidates:
            return False

        # 隨機選擇一塊成熟的作物
        target_r, target_c = random.choice(candidates)
        self.move_farmer_to(target_r, target_c)

        # 執行收穫
        self.harvest(target_r, target_c)
        return True

    def place_soil_and_plant(self):
        """
        隨機選擇一塊農地，移動農夫至該位置，放土並種植作物。
        """
        # 隨機選擇一塊農地
        r = random.randint(0, GRID_ROWS - 1)
        c = random.randint(0, GRID_COLS - 1)

        # 移動農夫至該位置
        self.move_farmer_to(r, c)

        # 放置泥土
        self.place_soil(r, c)

        # 種植作物
        self.plant_seed(r, c)

    def move_farmer_to(self, r, c):
        """
        直接將農夫移動至指定農地格子的中心位置。
        """
        # 計算目標位置的中心點座標
        target_x = (
            self.background.farm_grid_x
            + c * self.farm_grid.block_width
            + self.farm_grid.block_width // 2
            - self.farmer.image_width // 2  # 調整農夫位置使其置中
        )
        target_y = (
            self.background.farm_grid_y
            + r * self.farm_grid.block_height
            + self.farm_grid.block_height // 2
            - self.farmer.image_height // 2  # 調整農夫位置使其置中
        )

        # 直接設定農夫的位置
        self.farmer.x = target_x
        self.farmer.y = target_y

    def place_soil(self, r, c):
        """
        在指定農地放置泥土，若該格無泥土且金幣足夠。
        """
        dirt = self.dirt_grid[r][c]
        if dirt is None:
            # 放置新的泥土，成本為50金幣
            cost = 50
            if self.coin.get_amount() >= cost:
                dirt = Dirt(
                    grid_x=c,
                    grid_y=r,
                    farm_grid_x=self.background.farm_grid_x,
                    farm_grid_y=self.background.farm_grid_y,
                    block_width=self.farm_grid.block_width,
                    block_height=self.farm_grid.block_height,
                    level=0,
                )
                self.dirt_grid[r][c] = dirt
                self.coin.decrease(cost)
                print(f"Placed dirt at ({r}, {c}).")
            else:
                print("Insufficient coins to place dirt.")
        else:
            # 嘗試升級泥土
            if dirt.level < len(DIRT_LEVELS) - 1:
                upgrade_cost = DIRT_LEVELS[dirt.level]["upgrade_cost"]
                if self.coin.get_amount() >= upgrade_cost:
                    self.coin.decrease(upgrade_cost)
                    dirt.upgrade()
                    print(f"Upgraded dirt at ({r}, {c}) to level {dirt.level}.")
                else:
                    print("Insufficient coins to upgrade dirt.")
            else:
                print(f"Dirt at ({r}, {c}) is already at maximum level.")

    def plant_seed(self, r, c):
        """
        在指定農地種植作物，若該格有泥土且無作物且有種子。
        """
        dirt = self.dirt_grid[r][c]
        if dirt and dirt.plant is None:
            # 選擇一種種子（隨機選擇）
            available_seeds = [item for item in self.seed_inventory.items if item]
            if available_seeds:
                seed = random.choice(available_seeds)
                # 找出種子的索引
                seed_index = self.seed_inventory.items.index(seed)
                # 種植作物
                plant_image_path = "./img/CropSeed2.png"  # 可以根據種子種類調整
                plant = Plant(image_path=plant_image_path, scale=(64, 64))
                dirt.plant_seed(plant)
                # 庫存減1
                self.seed_inventory.quantities[seed_index] -= 1
                if self.seed_inventory.quantities[seed_index] == 0:
                    self.seed_inventory.items[seed_index] = None
                print(f"Planted {seed.name} at ({r}, {c}).")
            else:
                print("No seeds available to plant.")
        else:
            print(f"Cannot plant at ({r}, {c}). Either no dirt or already has a plant.")

    def harvest(self, r, c):
        """
        收穫指定農地的作物，若該作物已到達第5階段。
        """
        dirt = self.dirt_grid[r][c]
        if dirt and dirt.plant and dirt.plant.stage == 5:
            # 增加金幣
            self.coin.increase(50)
            print(f"Harvested plant at ({r}, {c}) and gained 50 coins.")
            # 移除作物
            dirt.plant = None

            # 創建收穫動畫
            coin_text = f"金幣：{self.coin.get_amount()}"
            coin_text_width, _ = self.font.size(coin_text)

            anim_x = 10 + coin_text_width + 10
            anim_y = 10

            animation = self.create_coin_animation(
                x=anim_x,
                y=anim_y,
                text="+50",
                color="#FF3E3E",
                duration=2000,
            )
            self.coin_animations.append(animation)
        else:
            print(f"No mature plant to harvest at ({r}, {c}).")

    def record_game_state(self, current_ticks):
        """
        每秒記錄一次遊戲狀態。
        包括每個土壤位置的資訊（座標、土壤等級、植物等級）、時間（秒數）、金幣數量。
        """
        # 計算經過的秒數
        elapsed_seconds = (current_ticks - self.start_time) // 1000

        # 確保每秒只記錄一次
        if elapsed_seconds > self.last_record_second:
            self.last_record_second = elapsed_seconds

            # 收集每個土壤位置的資訊
            for r in range(GRID_ROWS):
                for c in range(GRID_COLS):
                    dirt = self.dirt_grid[r][c]
                    if dirt is None:
                        soil_level = 0  # 沒有土壤
                        plant_level = 0  # 沒有植物
                    else:
                        soil_level = dirt.level + 1  # 1~4，根據 DIRT_LEVELS
                        plant_level = dirt.plant.stage if dirt.plant else 0  # 1~5 或 0

                    # 取得土壤圖片的座標（左上角）
                    soil_x = dirt.farm_grid_x + c * dirt.block_width if dirt else 0
                    soil_y = dirt.farm_grid_y + r * dirt.block_height if dirt else 0

                    # 構建數據字典
                    data_entry = {
                        "Time (s)": elapsed_seconds,
                        "Grid Row": r,
                        "Grid Column": c,
                        "Soil Level": soil_level,
                        "Plant Level": plant_level,
                        "Coins": self.coin.get_amount(),
                    }

                    self.game_data.append(data_entry)

    def save_game_data(self):
        """
        將收集到的遊戲數據儲存為 .csv 檔案。
        檔名包含遊戲開始時的時間。
        """
        if not self.game_data:
            print("No game data to save.")
            return

        # 創建 DataFrame
        df = pd.DataFrame(self.game_data)

        # 儲存為 .csv 檔案
        df.to_csv(self.csv_filename, index=False, encoding='utf-8-sig')
        print(f"Game data saved to {self.csv_filename}.")


if __name__ == "__main__":
    auto_game = AutoGame()
    auto_game.run()
