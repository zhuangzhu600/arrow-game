# 方向常量，用 (dx, dy) 表示
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# 棋盘行列数
ROWS = 5
COLS = 5

# 每关的失误次数上限
MAX_MISTAKES = 3


class Arrow:
    def __init__(self, row, col, direction):
        self.row = row          # 第几行
        self.col = col          # 第几列
        self.direction = direction  # 方向
        self.alive = True       # 是否还在棋盘上

    def __repr__(self):
        return f"Arrow(row={self.row}, col={self.col}, dir={self.direction})"


# 关卡数据：每个关卡是一个箭头列表
LEVELS = [
    # 第一关：3个箭头
    [
        Arrow(2, 2, RIGHT),
        Arrow(2, 0, RIGHT),
        Arrow(0, 0, DOWN),
    ],
    # 第二关：5个箭头
    [
        Arrow(2, 2, RIGHT),
        Arrow(2, 0, RIGHT),
        Arrow(0, 2, DOWN),
        Arrow(4, 0, UP),
        Arrow(0, 4, LEFT),
    ],
    # 第三关：7个箭头
    [
        Arrow(2, 2, RIGHT),
        Arrow(2, 0, RIGHT),
        Arrow(0, 2, DOWN),
        Arrow(4, 2, UP),
        Arrow(2, 4, LEFT),
        Arrow(0, 0, RIGHT),
        Arrow(4, 4, LEFT),
    ],
]