import random

# 方向常量，用 (行变化, 列变化) 表示
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)

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


def can_fly_out(arrow, level, rows, cols):
    """检查箭头前方是否没有阻挡"""
    dr, dc = arrow.direction
    r = arrow.row + dr
    c = arrow.col + dc
    while 0 <= r < rows and 0 <= c < cols:
        for other in level:
            if other.alive and other is not arrow and other.row == r and other.col == c:
                return False
        r += dr
        c += dc
    return True


def generate_random_level(rows, cols, num_arrows):
    """
    逆向生成一个保证有解的关卡。
    原理：从空棋盘开始，每次放置一个箭头时，要求它沿自身方向到棋盘
    边界之间没有任何已放置的箭头。这样所有箭头放完后，按照放置顺序
    的反序点击就能通关。
    为了增加难度，每次倾向于选择能挡住更多已有箭头的候选位置。
    """
    board = {}   # (row, col) -> Arrow
    arrows = []
    directions = [UP, DOWN, LEFT, RIGHT]

    for _ in range(num_arrows):
        candidates = []
        for r in range(rows):
            for c in range(cols):
                if (r, c) in board:
                    continue
                for d in directions:
                    dr, dc = d
                    nr, nc = r + dr, c + dc
                    free = True
                    while 0 <= nr < rows and 0 <= nc < cols:
                        if (nr, nc) in board:
                            free = False
                            break
                        nr += dr
                        nc += dc
                    if free:
                        # 打分：这个位置会挡住多少已有箭头
                        score = 0
                        for (br, bc), b_arrow in board.items():
                            bdr, bdc = b_arrow.direction
                            tr, tc = br + bdr, bc + bdc
                            while 0 <= tr < rows and 0 <= tc < cols:
                                if (tr, tc) == (r, c):
                                    score += 1
                                    break
                                tr += bdr
                                tc += bdc
                        candidates.append((score, r, c, d))

        if not candidates:
            break

        # 偏向高分候选，但保留随机性
        max_score = max(c[0] for c in candidates)
        top = [c for c in candidates if c[0] >= max_score - 1]
        score, r, c, d = random.choice(top)

        arrow = Arrow(r, c, d)
        board[(r, c)] = arrow
        arrows.append(arrow)

    return arrows