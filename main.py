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
ARROW_SELECTED = (230, 120, 60)
ARROW_HIT = (220, 60, 60)

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
selected_arrow = None
hit_arrow = None
hit_timer = 0
result_message = ""

# 失误次数
mistakes_left = MAX_MISTAKES

# 飞行中的箭头状态
flying_arrow = None
flying_x = 0
flying_y = 0
flying_speed = 12

# 按钮区域
start_btn_rect = pygame.Rect(WIDTH // 2 - 100, 350, 200, 60)
restart_btn_rect = pygame.Rect(20, HEIGHT - 60, 120, 40)  # 游戏中的重新开始按钮
result_restart_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 40, 100, 50)  # 结果界面的重开按钮
result_next_btn = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 40, 100, 50)  # 结果界面的下一关按钮


def cell_center(row, col):
    x = BOARD_LEFT + col * CELL_SIZE + CELL_SIZE // 2
    y = BOARD_TOP + row * CELL_SIZE + CELL_SIZE // 2
    return x, y


def pos_to_cell(pos):
    x, y = pos
    if x < BOARD_LEFT or x >= BOARD_LEFT + COLS * CELL_SIZE:
        return None
    if y < BOARD_TOP or y >= BOARD_TOP + ROWS * CELL_SIZE:
        return None
    col = (x - BOARD_LEFT) // CELL_SIZE
    row = (y - BOARD_TOP) // CELL_SIZE
    return int(row), int(col)


def find_arrow_at(row, col):
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

    # 左上角：关卡信息 + 失误次数
    info = FONT_SMALL.render(f"第 {current_level + 1} 关", True, TEXT_COLOR)
    screen.blit(info, (20, 20))

    mistakes_text = FONT_SMALL.render(f"剩余失误: {mistakes_left}", True, TEXT_COLOR)
    screen.blit(mistakes_text, (20, 50))

    draw_board()

    for arrow in LEVELS[current_level]:
        if arrow.alive:
            if arrow is flying_arrow:
                draw_arrow(flying_x, flying_y, arrow.direction, ARROW_COLOR)
            else:
                cx, cy = cell_center(arrow.row, arrow.col)
                if arrow is hit_arrow and hit_timer > 0:
                    draw_arrow(cx, cy, arrow.direction, ARROW_HIT)
                elif arrow is selected_arrow:
                    draw_arrow(cx, cy, arrow.direction, ARROW_SELECTED)
                else:
                    draw_arrow(cx, cy, arrow.direction, ARROW_COLOR)

    # 画重新开始按钮
    mouse_pos = pygame.mouse.get_pos()
    btn_color = BTN_HOVER if restart_btn_rect.collidepoint(mouse_pos) else BTN_COLOR
    pygame.draw.rect(screen, btn_color, restart_btn_rect, border_radius=5)
    restart_text = FONT_SMALL.render("重新开始", True, (255, 255, 255))
    screen.blit(restart_text, (restart_btn_rect.centerx - restart_text.get_width() // 2,
                               restart_btn_rect.centery - restart_text.get_height() // 2))

    back = FONT_SMALL.render("按 ESC 返回开始界面", True, (120, 120, 120))
    screen.blit(back, (WIDTH // 2 - back.get_width() // 2, HEIGHT - 40))


def draw_result_screen():
    screen.fill(BG_COLOR)
    tip = FONT_MID.render(result_message, True, TEXT_COLOR)
    screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 2 - 60))

    mouse_pos = pygame.mouse.get_pos()

    # 画重开按钮
    color = BTN_HOVER if result_restart_btn.collidepoint(mouse_pos) else BTN_COLOR
    pygame.draw.rect(screen, color, result_restart_btn, border_radius=10)
    restart_text = FONT_SMALL.render("重新开始", True, (255, 255, 255))
    screen.blit(restart_text, (result_restart_btn.centerx - restart_text.get_width() // 2,
                               result_restart_btn.centery - restart_text.get_height() // 2))

    # 如果通关了，才画“下一关”按钮
    if result_message == "通关！":
        color = BTN_HOVER if result_next_btn.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(screen, color, result_next_btn, border_radius=10)
        next_text = FONT_SMALL.render("下一关", True, (255, 255, 255))
        screen.blit(next_text, (result_next_btn.centerx - next_text.get_width() // 2,
                                result_next_btn.centery - next_text.get_height() // 2))


def reset_level():
    """把当前关卡恢复到初始状态"""
    global mistakes_left, selected_arrow, hit_arrow, hit_timer, flying_arrow
    mistakes_left = MAX_MISTAKES
    selected_arrow = None
    hit_arrow = None
    hit_timer = 0
    flying_arrow = None
    for arrow in LEVELS[current_level]:
        arrow.alive = True


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if state == STATE_PLAYING:
                    state = STATE_START
                    selected_arrow = None
                    hit_arrow = None
                    hit_timer = 0
                    flying_arrow = None
                elif state == STATE_RESULT:
                    state = STATE_START
                    current_level = 0
                    reset_level()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == STATE_START:
                if start_btn_rect.collidepoint(event.pos):
                    state = STATE_PLAYING
                    current_level = 0
                    reset_level()

            elif state == STATE_PLAYING:
                # 先判断是否点了重新开始
                if restart_btn_rect.collidepoint(event.pos):
                    reset_level()
                elif flying_arrow is None:
                    cell = pos_to_cell(event.pos)
                    if cell:
                        row, col = cell
                        arrow = find_arrow_at(row, col)
                        if arrow:
                            selected_arrow = arrow
                            if can_fly_out(arrow, LEVELS[current_level]):
                                flying_arrow = arrow
                                flying_x, flying_y = cell_center(arrow.row, arrow.col)
                                selected_arrow = None
                            else:
                                hit_arrow = arrow
                                hit_timer = 20
                                mistakes_left -= 1
                                if mistakes_left <= 0:
                                    state = STATE_RESULT
                                    result_message = "游戏失败！"
                                    selected_arrow = None
                        else:
                            selected_arrow = None

            elif state == STATE_RESULT:
                if result_restart_btn.collidepoint(event.pos):
                    reset_level()
                    state = STATE_PLAYING
                elif result_message == "通关！" and result_next_btn.collidepoint(event.pos):
                    current_level += 1
                    if current_level >= len(LEVELS):
                        current_level = 0  # 最后一关通关后，回到第一关
                    reset_level()
                    state = STATE_PLAYING

    if flying_arrow is not None:
        dr, dc = flying_arrow.direction
        flying_x += dc * flying_speed
        flying_y += dr * flying_speed

        if (flying_x < BOARD_LEFT - CELL_SIZE or
            flying_x > BOARD_LEFT + COLS * CELL_SIZE + CELL_SIZE or
            flying_y < BOARD_TOP - CELL_SIZE or
            flying_y > BOARD_TOP + ROWS * CELL_SIZE + CELL_SIZE):
            flying_arrow.alive = False
            flying_arrow = None

    # 检查是否通关（所有箭头都不在棋盘上，并且没有正在飞的箭头）
    if state == STATE_PLAYING:
        all_dead = True
        for arrow in LEVELS[current_level]:
            if arrow.alive:
                all_dead = False
                break
        if all_dead and flying_arrow is None:
            state = STATE_RESULT
            result_message = "通关！"

    if state == STATE_START:
        draw_start_screen()
    elif state == STATE_PLAYING:
        draw_playing_screen()
    elif state == STATE_RESULT:
        draw_result_screen()

    if hit_timer > 0:
        hit_timer -= 1
    else:
        hit_arrow = None

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()