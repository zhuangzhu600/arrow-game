# 当前界面模式：start / level_select / playing / result
mode = "start"

# 棋盘布局（会随关卡变化）
ROWS = 5
COLS = 5
CELL_SIZE = 90
BOARD_LEFT = 0
BOARD_TOP = 0

# 当前关卡
current_level = 0
level_arrows = []

# 游戏过程中的状态
selected_arrow = None
hit_arrow = None
hit_timer = 0
result_message = ""
mistakes_left = 3
flying_arrow = None
flying_x = 0
flying_y = 0
flying_speed = 12
level_start_time = 0
elapsed_time = 0.0
stars_earned = 0
history = []
reset_confirm = False

# 存档数据（在 main.py 里加载）
save_data = None