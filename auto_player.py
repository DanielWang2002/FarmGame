import random
import datetime
import os

import pygame
import pandas as pd
from pathlib import Path
import multiprocessing
import argparse
import os
import sys
import csv  # 新增：用於寫 CSV

from dirt import Dirt
from main_game import Game
from settings import GRID_ROWS, GRID_COLS, DIRT_LEVELS
from plant import Plant

os.environ["SDL_VIDEODRIVER"] = "dummy"


class AutoGame(Game):
    """
    自動化代理類別，繼承自 Game，直接控制農夫移動並執行動作。
    """
    def __init__(self, instance_id=1, speed_multiplier=1):
        super().__init__()
        self.total_time = 60  # 60 秒
        self.FPS = 60
        self.next_action_time = 0
        self.game_data = []
        self.last_record_second = -1
        self.game_start_datetime = datetime.datetime.now()
        self.csv_filename = f"log/game_{self.game_start_datetime.strftime('%Y%m%d_%H%M%S')}_instance{instance_id}.csv"
        Path("log").mkdir(exist_ok=True)
        
        self.game_time = 0
        self.speed_multiplier = speed_multiplier
        self.last_frame_ticks = pygame.time.get_ticks()
        self.instance_id = instance_id

    def run(self):
        """
        覆寫 Game.run()，加入自動化動作流程和數據收集。
        回傳最終金幣 (final_coin) 以便父進程可得知結果。
        """
        while True:
            current_ticks = pygame.time.get_ticks()
            delta_ticks = current_ticks - self.last_frame_ticks
            delta_seconds = delta_ticks / 1000.0
            self.game_time += delta_seconds * self.speed_multiplier
            self.last_frame_ticks = current_ticks

            if self.game_time >= self.total_time:
                # 在遊戲結束前記錄最後一秒的狀態
                self.record_game_state(self.game_time)

                final_coin = self.coin.get_amount()
                print(f"[Instance {self.instance_id}] Time's up! Final coin count = {final_coin}")

                # 儲存數據
                #self.save_game_data()
                pygame.quit()

                # 回傳最終金幣給父進程
                return final_coin

            if self.game_time >= self.next_action_time:
                self.do_random_action()
                self.next_action_time = self.game_time + random.randint(2, 5)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_game_data()
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            self.farmer.update(keys)

            self.update_seeds()
            self.update_plants_growth()

            for animation in self.coin_animations[:]:
                animation.update()
                if animation.alpha <= 0:
                    self.coin_animations.remove(animation)

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

            self.record_game_state(self.game_time)

    # ---- 以下為自動動作相關方法省略不變 ----
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
        self.harvest(target_r, target_c)
        self.place_soil_and_plant()
        return True

    def place_soil_and_plant(self):
        """
        隨機選擇一塊農地，移動農夫至該位置，放土並種植作物。
        """
        # 隨機選擇一塊農地
        r = random.randint(0, GRID_ROWS - 1)
        c = random.randint(0, GRID_COLS - 1)
        self.move_farmer_to(r, c)
        self.place_soil(r, c)
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
            - self.farmer.image_width // 2
        )
        target_y = (
            self.background.farm_grid_y
            + r * self.farm_grid.block_height
            + self.farm_grid.block_height // 2
            - self.farmer.image_height // 2
        )
        self.farmer.x = target_x
        self.farmer.y = target_y

    def place_soil(self, r, c):
        """
        在指定農地放置泥土，若該格無泥土且金幣足夠。
        """
        dirt = self.dirt_grid[r][c]
        if dirt is None:
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
                print(f"[Instance {self.instance_id}] Placed dirt at ({r}, {c}).")
            else:
                print(f"[Instance {self.instance_id}] Insufficient coins to place dirt.")
        else:
            if dirt.level < len(DIRT_LEVELS) - 1:
                upgrade_cost = DIRT_LEVELS[dirt.level]["upgrade_cost"]
                if self.coin.get_amount() >= upgrade_cost:
                    self.coin.decrease(upgrade_cost)
                    dirt.upgrade()
                    print(f"[Instance {self.instance_id}] Upgraded dirt at ({r}, {c}) to level {dirt.level}.")
                else:
                    print(f"[Instance {self.instance_id}] Insufficient coins to upgrade dirt.")
            else:
                print(f"[Instance {self.instance_id}] Dirt at ({r}, {c}) is already at maximum level.")

    def plant_seed(self, r, c):
        dirt = self.dirt_grid[r][c]
        if dirt and dirt.plant is None:
            available_seeds = [item for item in self.seed_inventory.items if item]
            if available_seeds:
                seed = random.choice(available_seeds)
                seed_index = self.seed_inventory.items.index(seed)
                plant_image_path = "./img/CropSeed2.png"
                plant = Plant(image_path=plant_image_path, scale=(64, 64))
                dirt.plant_seed(plant)
                self.seed_inventory.quantities[seed_index] -= 1
                if self.seed_inventory.quantities[seed_index] == 0:
                    self.seed_inventory.items[seed_index] = None
                print(f"[Instance {self.instance_id}] Planted {seed.name} at ({r}, {c}).")
            else:
                print(f"[Instance {self.instance_id}] No seeds available to plant.")
        else:
            print(f"[Instance {self.instance_id}] Cannot plant at ({r}, {c}). Either no dirt or already has a plant.")
            

    def harvest(self, r, c):
        dirt = self.dirt_grid[r][c]
        if dirt and dirt.plant and dirt.plant.stage == 5:
            self.coin.increase(50)
            print(f"[Instance {self.instance_id}] Harvested plant at ({r}, {c}) and gained 50 coins.")
            dirt.plant = None
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
            print(f"[Instance {self.instance_id}] No mature plant to harvest at ({r}, {c}).")

    def record_game_state(self, game_time):
        elapsed_seconds = int(game_time)
        if elapsed_seconds > self.last_record_second:
            self.last_record_second = elapsed_seconds
            for r in range(GRID_ROWS):
                for c in range(GRID_COLS):
                    dirt = self.dirt_grid[r][c]
                    if dirt is None:
                        soil_level = 0
                        plant_level = 0
                    else:
                        soil_level = dirt.level + 1
                        plant_level = dirt.plant.stage if dirt.plant else 0

                    data_entry = {
                        "Time (s)": elapsed_seconds,
                        "Grid Row": r,
                        "Grid Column": c,
                        "Soil Level": soil_level,
                        "Plant Level": plant_level,
                        "Coins": self.coin.get_amount(),
                        "Instance ID": self.instance_id,
                    }
                    self.game_data.append(data_entry)

    def save_game_data(self):
        if not self.game_data:
            print(f"[Instance {self.instance_id}] No game data to save.")
            return
        df = pd.DataFrame(self.game_data)
        df.to_csv(self.csv_filename, index=False, encoding='utf-8-sig')
        print(f"[Instance {self.instance_id}] Game data saved to {self.csv_filename}.")


def worker(instance_id, speed_multiplier, results_queue):
    """
    子進程的工作函式：
    1. 執行 AutoGame
    2. 取得 final_coin
    3. 將 (instance_id, final_coin) 放入 results_queue
    """
    game = AutoGame(instance_id=instance_id, speed_multiplier=speed_multiplier)
    final_coin = game.run()  # Game.run() 會 return 最終金幣
    results_queue.put((instance_id, final_coin))  # 回傳結果給父進程


def run_auto_game(instance_id, speed_multiplier):
    """
    如果你單純想在不啟用多進程下，直接執行一個 AutoGame 實例，可使用此函式。
    但現在我們改用 worker() + Queue 的方式。
    """
    game = AutoGame(instance_id=instance_id, speed_multiplier=speed_multiplier)
    final_coin = game.run()
    return final_coin


def main():
    """
    主函數，解析命令行參數並啟動多個 AutoGame 實例。
    最後將所有結果寫入 CSV。
    """
    parser = argparse.ArgumentParser(description="啟動多個 AutoGame 實例。")
    parser.add_argument(
        "-n",
        "--num_instances",
        type=int,
        default=20,
        help="啟動的 AutoGame 實例數量（預設為 1）。",
    )
    parser.add_argument(
        "-s",
        "--speed_multiplier",
        type=float,
        default=1.0,
        help="遊戲速度倍數（預設為 1.0）。",
    )
    args = parser.parse_args()

    num_instances = args.num_instances
    speed_multiplier = args.speed_multiplier

    if num_instances < 1:
        print("實例數量必須大於等於 1。")
        sys.exit(1)

    # 建立 Queue，用來接收子進程的 (instance_id, final_coin)
    results_queue = multiprocessing.Queue()

    processes = []
    for i in range(1, num_instances + 1):
        p = multiprocessing.Process(target=worker, args=(i, speed_multiplier, results_queue))
        p.start()
        processes.append(p)
        print(f"啟動 AutoGame 實例 {i}，速度倍數 {speed_multiplier}x。")

    # 等待所有進程結束
    for p in processes:
        p.join()

    # 統一收集結果
    results = []
    while not results_queue.empty():
        results.append(results_queue.get())
    # results 內容類似 [(1, final_coin1), (2, final_coin2), ...]

    # 為了讓結果有序，可用 instance_id 排序
    results.sort(key=lambda x: x[0])

    # 將結果寫入 CSV
    # 每一行加上 "執行編號 (instance_id)" 以及對應的 "final_coin"
    output_csv = "initial_amount_100.csv"
    final_data = []
    for instance_id, final_coin in results:
        constants = {
            "Instance ID": instance_id,
            "Final Coin": final_coin,
            "initial_amount": 100,
            "DIRT_Newcost": 50,
            "DIRT_Normal_upgrade_cost": 20,
            "DIRT_Normal_speed_bonus": 0,
            "DIRT_Plus_upgrade_cost": 60,
            "DIRT_Plus_speed_bonus": 0.05,
            "DIRT_Extra_upgrade_cost": 115,
            "DIRT_Extra_speed_bonus": 0.1,
            "DIRT_Ultra_upgrade_cost": 0,
            "DIRT_Ultra_speed_bonus": 0.2,
        }
        final_data.append(constants)

    df = pd.DataFrame(final_data)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"所有子進程執行完畢，結果已儲存至 {output_csv}")


if __name__ == "__main__":
    main()
