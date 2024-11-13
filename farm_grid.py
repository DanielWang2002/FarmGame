# farm_grid.py

from settings import GRID_ROWS, GRID_COLS


class FarmGrid:
    def __init__(self, background):
        # 設定圖片位置，從 background 中取得農地圖片的起始位置和大小
        self.farm_grid_x = background.farm_grid_x
        self.farm_grid_y = background.farm_grid_y
        self.block_width = background.farm_grid.get_width() // GRID_COLS
        self.block_height = background.farm_grid.get_height() // GRID_ROWS

    def get_grid_position(self, x, y):
        # 計算農夫相對於網格的位移
        relative_x = x - self.farm_grid_x
        relative_y = y - self.farm_grid_y
        grid_x = int(relative_x // self.block_width)
        grid_y = int(relative_y // self.block_height)

        # 檢查位置是否在網格範圍內
        if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:
            return grid_x, grid_y
        return None
