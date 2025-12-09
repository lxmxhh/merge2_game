import pygame

# 游戏配置
ROWS = 6
COLS = 6
TILE_SIZE = 60
MARGIN = 12
HEADER = 110

# 计算窗口大小
GRID_AREA_W = COLS * TILE_SIZE + (COLS + 1) * MARGIN
GRID_AREA_H = ROWS * TILE_SIZE + (ROWS + 1) * MARGIN
WIDTH = GRID_AREA_W + 2 * MARGIN
HEIGHT = HEADER + GRID_AREA_H + MARGIN
FPS = 60

# 颜色配置
BG_COLOR = (250, 248, 239)
GRID_BG = (187, 173, 160)
EMPTY_COLOR = (205, 193, 180)
TEXT_COLOR_DARK = (119, 110, 101)
TEXT_COLOR_LIGHT = (249, 246, 242)
SCORE_BG = (143, 122, 102)
SELECTED_BORDER_COLOR = (255, 215, 0)
OVERLAY_COLOR = (255, 255, 255, 200)
MAXED_TILE_BG = (160, 160, 160)

# 等级名称
LEVEL_NAMES = {
    1: "E1",
    2: "E2",
    3: "E3",
    4: "E4",
    5: "E5",
    6: "E6",
    7: "E7",
    8: "E8",
    9: "E9",
}

# 默认等级颜色
TILE_COLORS = {
    1: (238, 228, 218),
    2: (237, 224, 200),
    3: (242, 177, 121),
    4: (245, 149, 99),
    5: (246, 124, 95),
    6: (246, 94, 59),
}

# 可选：为每种道具配置最高等级；留空则从 assets 中自动检测
ITEM_MAX_LEVELS = {
    # 例如：1: 6, 2: 5, 3: 4
}
