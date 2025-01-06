# settings.py

# 視窗設置
WINDOW_WIDTH = 1440
WINDOW_HEIGHT = 810
FPS = 60

# 顏色定義
WHITE = (255, 255, 255)

# 農田網格設定
GRID_ROWS = 3
GRID_COLS = 6
BLOCK_WIDTH = 100  # 每個區塊的寬度
BLOCK_HEIGHT = 100  # 每個區塊的高度

# 各項泥土參數
DIRT_LEVELS = [
    {
        "name": "Normal",
        "image": "./img/Dirt_Normal.png",
        "upgrade_cost": 20,  # 升級到下一級的費用
        "growth_speed_bonus": 0,
    },
    {
        "name": "Plus",
        "image": "./img/Dirt_Plus.png",
        "upgrade_cost": 60,
        "growth_speed_bonus": 0.05,
    },
    {
        "name": "Extra",
        "image": "./img/Dirt_Extra.png",
        "upgrade_cost": 115,
        "growth_speed_bonus": 0.10,
    },
    {
        "name": "Ultra",
        "image": "./img/Dirt_Ultra.png",
        "upgrade_cost": 0,  # 無法再升級
        "growth_speed_bonus": 0.20,
    },
]
