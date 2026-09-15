# 窗口尺寸
WIDTH, HEIGHT = 800, 800

# 颜色
BG_COLOR = (240, 240, 240)
TEXT_COLOR = (50, 50, 50)
BTN_COLOR = (100, 160, 220)
BTN_HOVER = (70, 130, 200)
BTN_LOCKED = (190, 190, 190)
BTN_DANGER = (220, 80, 80)
BTN_DANGER_HOVER = (200, 50, 50)
ARROW_COLOR = (60, 90, 140)
ARROW_SELECTED = (230, 120, 60)
ARROW_HIT = (220, 60, 60)
CELL_BG_COLOR = (225, 235, 245)
ARROW_SHADOW = (200, 200, 200)

# 游戏常量
MAX_MISTAKES = 3

# 关卡配置：(行, 列, 最少箭头, 最多箭头)
LEVEL_CONFIGS = [
    (5, 5, 6, 8),
    (6, 6, 9, 12),
    (7, 7, 13, 16),
    (8, 8, 17, 21),
    (9, 9, 21, 26),
]

# 状态字符串
STATE_START = "start"
STATE_LEVEL_SELECT = "level_select"
STATE_PLAYING = "playing"
STATE_RESULT = "result"

# 字体（延迟初始化，在 pygame.init() 之后调用 init_fonts()）
FONT_BIG = None
FONT_MID = None
FONT_SMALL = None
FONT_TINY = None


def init_fonts():
    global FONT_BIG, FONT_MID, FONT_SMALL, FONT_TINY
    import pygame
    FONT_BIG = pygame.font.SysFont("simhei", 48)
    FONT_MID = pygame.font.SysFont("simhei", 28)
    FONT_SMALL = pygame.font.SysFont("simhei", 22)
    FONT_TINY = pygame.font.SysFont("simhei", 18)