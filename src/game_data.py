import random

UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)


class Arrow:
    def __init__(self, row, col, direction):
        self.row = row
        self.col = col
        self.direction = direction
        self.alive = True


def can_fly_out(arrow, level, rows, cols):
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


def generate_random_level(rows, cols, num_arrows, seed=None):
    if seed is not None:
        random.seed(seed)

    board = {}
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

        max_score = max(c[0] for c in candidates)
        top = [c for c in candidates if c[0] >= max_score - 1]
        score, r, c, d = random.choice(top)

        arrow = Arrow(r, c, d)
        board[(r, c)] = arrow
        arrows.append(arrow)

    return arrows

def calculate_stars(time_used, mistakes_used):
        if time_used <= 20 and mistakes_used == 0:
            return 3
        elif time_used <= 40 and mistakes_used <= 1:
            return 2
        else:
            return 1