# 方向常量，用 (行变化, 列变化) 表示
UP = (-1, 0)     # 行减1，列不变
DOWN = (1, 0)    # 行加1，列不变
LEFT = (0, -1)   # 行不变，列减1
RIGHT = (0, 1)   # 行不变，列加1

# 棋盘行列数
ROWS = 5
COLS = 5

# 每关的失误次数上限
MAX_MISTAKES = 3


class Arrow:
    def __init__(self, row, col, direction):
        self.row = row
        self.col = col
        self.direction = direction
        self.alive = True

    def __repr__(self):
        return f"Arrow(row={self.row}, col={self.col}, dir={self.direction})"


def can_fly_out(arrow, level):
    """
    检查箭头前方是否没有阻挡。
    沿箭头方向一格一格往外走，遇到还活着的箭头就返回 False，
    走出棋盘都没遇到就返回 True。
    """
    dr, dc = arrow.direction
    r = arrow.row + dr
    c = arrow.col + dc
    while 0 <= r < ROWS and 0 <= c < COLS:
        for other in level:
            if other.alive and other is not arrow and other.row == r and other.col == c:
                return False
        r += dr
        c += dc
    return True


# 关卡数据
LEVELS = [
    [
        Arrow(2, 2, RIGHT),
        Arrow(2, 0, RIGHT),
        Arrow(0, 0, DOWN),
    ],
    [
        Arrow(2, 2, RIGHT),
        Arrow(2, 0, RIGHT),
        Arrow(0, 2, DOWN),
        Arrow(4, 0, UP),
        Arrow(0, 4, LEFT),
    ],
    [
        Arrow(2, 4, RIGHT),  # 1. 最右侧，向右飞，无阻碍
        Arrow(4, 0, RIGHT),  # 2. 最左下角，向右飞，无阻碍（独立）
        Arrow(2, 2, RIGHT),  # 3. 中间，向右飞，被(2,4)挡，等它飞走
        Arrow(2, 0, RIGHT),  # 4. 最左侧，向右飞，被(2,2)挡，等它飞走
        Arrow(0, 2, DOWN),  # 5. 正上方，向下飞，被(2,2)挡，等它飞走
    ],
]