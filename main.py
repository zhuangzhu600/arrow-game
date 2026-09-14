import pygame
import sys

from game_data import *

pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")
clock = pygame.time.Clock()

# 颜色
BG_COLOR = (240, 240, 240)
TEXT_COLOR = (50, 50, 50)
BTN_COLOR = (100, 160, 220)
BTN_HOVER = (70, 130, 200)
GRID_COLOR = (200, 200, 200)
ARROW_COLOR = (60, 90, 140)
ARROW_SELECTED = (230, 120, 60)   # 选中时的颜色（橙色）

# 字体
FONT_BIG = pygame.font.SysFont("simhei", 48)
FONT_MID = pygame.font.SysFont("simhei", 28)
FONT_SMALL = pygame.font.SysFont("simhei", 22)

# 棋盘布局
CELL_SIZE = 90
BOARD_LEFT = (WIDTH - COLS * CELL_SIZE) // 2
BOARD_TOP = 100

# 游戏状态
STATE_START = "start"
STATE_PLAYING = "playing"
STATE_RESULT = "result"
state = STATE_START

current_level = 0
selected_arrow = None   # 当前被选中的箭头对象，没有就是 None

start_btn_rect = pygame.Rect(WIDTH // 2 - 100, 350, 200, 60)


def cell_center(row, col):
    x = BOARD_LEFT + col * CELL_SIZE + CELL_SIZE // 2
    y = BOARD_TOP + row * CELL_SIZE + CELL_SIZE // 2
    return x, y


def pos_to_cell(pos):
    """把鼠标坐标转换成 (row, col)，如果不在棋盘上返回 None"""
    x, y = pos
    if x < BOARD_LEFT or x >= BOARD_LEFT + COLS * CELL_SIZE:
        return None
    if y < BOARD_TOP or y >= BOARD_TOP + ROWS * CELL_SIZE:
        return None
    col = (x - BOARD_LEFT) // CELL_SIZE
    row = (y - BOARD_TOP) // CELL_SIZE
    return int(row), int(col)


def find_arrow_at(row, col):
    """在指定格子里找还活着的箭头"""
    for arrow in LEVELS[current_level]:
        if arrow.alive and arrow.row == row and arrow.col == col:
            return arrow
    return None


def draw_arrow(cx, cy, direction, color):
    size = 44
    if direction == RIGHT:
        pts = [(cx + size // 2, cy),
               (cx - size // 2, cy - size // 2),
               (cx - size // 2, cy + size // 2)]
    elif direction == LEFT:
        pts = [(cx - size // 2, cy),
               (cx + size // 2, cy - size // 2),
               (cx + size // 2, cy + size // 2)]
    elif direction == UP:
        pts = [(cx, cy - size // 2),
               (cx - size // 2, cy + size // 2),
               (cx + size // 2, cy + size // 2)]
    elif direction == DOWN:
        pts = [(cx, cy + size // 2),
               (cx - size // 2, cy - size // 2),
               (cx + size // 2, cy - size // 2)]
    else:
        return
    pygame.draw.polygon(screen, color, pts)


def draw_board():
    for r in range(ROWS + 1):
        y = BOARD_TOP + r * CELL_SIZE
        pygame.draw.line(screen, GRID_COLOR,
                         (BOARD_LEFT, y),
                         (BOARD_LEFT + COLS * CELL_SIZE, y), 2)
    for c in range(COLS + 1):
        x = BOARD_LEFT + c * CELL_SIZE
        pygame.draw.line(screen, GRID_COLOR,
                         (x, BOARD_TOP),
                         (x, BOARD_TOP + ROWS * CELL_SIZE), 2)


def draw_start_screen():
    screen.fill(BG_COLOR)
    title = FONT_BIG.render("一箭又一箭", True, TEXT_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 180))

    mouse_pos = pygame.mouse.get_pos()
    color = BTN_HOVER if start_btn_rect.collidepoint(mouse_pos) else BTN_COLOR
    pygame.draw.rect(screen, color, start_btn_rect, border_radius=10)

    btn_text = FONT_MID.render("开始游戏", True, (255, 255, 255))
    screen.blit(btn_text, (start_btn_rect.centerx - btn_text.get_width() // 2,
                           start_btn_rect.centery - btn_text.get_height() // 2))


def draw_playing_screen():
    screen.fill(BG_COLOR)

    info = FONT_SMALL.render(f"第 {current_level + 1} 关", True, TEXT_COLOR)
    screen.blit(info, (20, 20))

    draw_board()

    for arrow in LEVELS[current_level]:
        if arrow.alive:
            cx, cy = cell_center(arrow.row, arrow.col)
            # 如果这个箭头被选中，用高亮色画
            if arrow is selected_arrow:
                draw_arrow(cx, cy, arrow.direction, ARROW_SELECTED)
            else:
                draw_arrow(cx, cy, arrow.direction, ARROW_COLOR)

    back = FONT_SMALL.render("按 ESC 返回开始界面", True, (120, 120, 120))
    screen.blit(back, (WIDTH // 2 - back.get_width() // 2, HEIGHT - 40))


def draw_result_screen():
    screen.fill(BG_COLOR)
    tip = FONT_MID.render("结果界面（待开发）", True, TEXT_COLOR)
    screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 2 - 20))


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and state == STATE_PLAYING:
                state = STATE_START
                selected_arrow = None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == STATE_START:
                if start_btn_rect.collidepoint(event.pos):
                    state = STATE_PLAYING

            elif state == STATE_PLAYING:
                cell = pos_to_cell(event.pos)
                if cell:
                    row, col = cell
                    arrow = find_arrow_at(row, col)
                    if arrow:
                        selected_arrow = arrow
                    else:
                        selected_arrow = None

    if state == STATE_START:
        draw_start_screen()
    elif state == STATE_PLAYING:
        draw_playing_screen()
    elif state == STATE_RESULT:
        draw_result_screen()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()