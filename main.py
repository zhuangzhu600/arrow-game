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
CELL_BG_COLOR = (225, 235, 245)
ARROW_SHADOW = (200, 200, 200)

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

# 新增：计时和星级相关
level_start_time = 0      # 当前关卡开始的时间
elapsed_time = 0.0        # 当前关卡已经用了多少秒
stars_earned = 0          # 通关时获得的星级（1~3）

# 操作历史记录（撤销用）
history = []

# 按钮区域
start_btn_rect = pygame.Rect(WIDTH // 2 - 100, 350, 200, 60)
restart_btn_rect = pygame.Rect(20, HEIGHT - 60, 120, 40)
undo_btn_rect = pygame.Rect(WIDTH - 140, HEIGHT - 60, 120, 40)
result_restart_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 40, 100, 50)
result_next_btn = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 40, 100, 50)


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


def draw_board():
    for r in range(ROWS):
        for c in range(COLS):
            x = BOARD_LEFT + c * CELL_SIZE
            y = BOARD_TOP + r * CELL_SIZE
            rect = pygame.Rect(x + 4, y + 4, CELL_SIZE - 8, CELL_SIZE - 8)
            pygame.draw.rect(screen, CELL_BG_COLOR, rect, border_radius=10)


def draw_arrow(cx, cy, direction, color):
    size = 40

    def get_pts(offset_x, offset_y):
        if direction == RIGHT:
            return [(cx + size // 2 + offset_x, cy + offset_y),
                    (cx - size // 2 + offset_x, cy - size // 2 + offset_y),
                    (cx - size // 2 + offset_x, cy + size // 2 + offset_y)]
        elif direction == LEFT:
            return [(cx - size // 2 + offset_x, cy + offset_y),
                    (cx + size // 2 + offset_x, cy - size // 2 + offset_y),
                    (cx + size // 2 + offset_x, cy + size // 2 + offset_y)]
        elif direction == UP:
            return [(cx + offset_x, cy - size // 2 + offset_y),
                    (cx - size // 2 + offset_x, cy + size // 2 + offset_y),
                    (cx + size // 2 + offset_x, cy + size // 2 + offset_y)]
        elif direction == DOWN:
            return [(cx + offset_x, cy + size // 2 + offset_y),
                    (cx - size // 2 + offset_x, cy - size // 2 + offset_y),
                    (cx + size // 2 + offset_x, cy - size // 2 + offset_y)]
        return []

    shadow_pts = get_pts(3, 3)
    if shadow_pts:
        pygame.draw.polygon(screen, ARROW_SHADOW, shadow_pts)

    pts = get_pts(0, 0)
    if pts:
        pygame.draw.polygon(screen, color, pts)


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

    mistakes_text = FONT_SMALL.render(f"剩余失误: {mistakes_left}", True, TEXT_COLOR)
    screen.blit(mistakes_text, (20, 50))

    arrows_left = 0
    for arrow in LEVELS[current_level]:
        if arrow.alive:
            arrows_left += 1
    arrows_text = FONT_SMALL.render(f"剩余箭头: {arrows_left}", True, TEXT_COLOR)
    screen.blit(arrows_text, (20, 80))

    # 新增：显示当前已用时
    time_text = FONT_SMALL.render(f"用时: {elapsed_time:.1f} 秒", True, TEXT_COLOR)
    screen.blit(time_text, (WIDTH - 180, 20))

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

    mouse_pos = pygame.mouse.get_pos()

    btn_color = BTN_HOVER if restart_btn_rect.collidepoint(mouse_pos) else BTN_COLOR
    pygame.draw.rect(screen, btn_color, restart_btn_rect, border_radius=5)
    restart_text = FONT_SMALL.render("重新开始", True, (255, 255, 255))
    screen.blit(restart_text, (restart_btn_rect.centerx - restart_text.get_width() // 2,
                               restart_btn_rect.centery - restart_text.get_height() // 2))

    undo_color = BTN_HOVER if undo_btn_rect.collidepoint(mouse_pos) else BTN_COLOR
    if flying_arrow is not None or not history:
        undo_color = (180, 180, 180)
    pygame.draw.rect(screen, undo_color, undo_btn_rect, border_radius=5)
    undo_text = FONT_SMALL.render("撤销", True, (255, 255, 255))
    screen.blit(undo_text, (undo_btn_rect.centerx - undo_text.get_width() // 2,
                            undo_btn_rect.centery - undo_text.get_height() // 2))

    back = FONT_SMALL.render("按 ESC 返回开始界面", True, (120, 120, 120))
    screen.blit(back, (WIDTH // 2 - back.get_width() // 2, HEIGHT - 20))


def draw_result_screen():
    screen.fill(BG_COLOR)

    if result_message == "通关！":
        # 显示通关、时间和星级
        tip = FONT_MID.render(f"通关！用时 {elapsed_time:.1f} 秒", True, TEXT_COLOR)
        screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 2 - 100))

        star_str = "★" * stars_earned + "☆" * (3 - stars_earned)
        star_text = FONT_BIG.render(star_str, True, (240, 180, 50))
        screen.blit(star_text, (WIDTH // 2 - star_text.get_width() // 2, HEIGHT // 2 - 50))
    else:
        tip = FONT_MID.render("游戏失败！", True, TEXT_COLOR)
        screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 2 - 60))

    mouse_pos = pygame.mouse.get_pos()

    color = BTN_HOVER if result_restart_btn.collidepoint(mouse_pos) else BTN_COLOR
    pygame.draw.rect(screen, color, result_restart_btn, border_radius=10)
    restart_text = FONT_SMALL.render("重新开始", True, (255, 255, 255))
    screen.blit(restart_text, (result_restart_btn.centerx - restart_text.get_width() // 2,
                               result_restart_btn.centery - restart_text.get_height() // 2))

    if result_message == "通关！":
        color = BTN_HOVER if result_next_btn.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(screen, color, result_next_btn, border_radius=10)
        next_text = FONT_SMALL.render("下一关", True, (255, 255, 255))
        screen.blit(next_text, (result_next_btn.centerx - next_text.get_width() // 2,
                                result_next_btn.centery - next_text.get_height() // 2))


def calculate_stars(time_used, mistakes_used):
    """根据时间和失误次数算星级，返回 1~3"""
    if time_used <= 20 and mistakes_used == 0:
        return 3
    elif time_used <= 40 and mistakes_used <= 1:
        return 2
    else:
        return 1


def reset_level():
    global mistakes_left, selected_arrow, hit_arrow, hit_timer, flying_arrow, history
    global level_start_time, elapsed_time, stars_earned
    mistakes_left = MAX_MISTAKES
    selected_arrow = None
    hit_arrow = None
    hit_timer = 0
    flying_arrow = None
    history = []
    elapsed_time = 0.0
    stars_earned = 0
    level_start_time = pygame.time.get_ticks()  # 重置起始时间
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
                    history = []
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
                if restart_btn_rect.collidepoint(event.pos):
                    reset_level()
                elif undo_btn_rect.collidepoint(event.pos):
                    if flying_arrow is None and history:
                        action_type, arrow = history.pop()
                        if action_type == 'fly':
                            arrow.alive = True
                        elif action_type == 'hit':
                            mistakes_left += 1
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
                                history.append(('fly', arrow))
                            else:
                                hit_arrow = arrow
                                hit_timer = 20
                                mistakes_left -= 1
                                history.append(('hit', None))
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
                        current_level = 0
                    reset_level()
                    state = STATE_PLAYING

    # 更新游戏内计时
    if state == STATE_PLAYING:
        elapsed_time = (pygame.time.get_ticks() - level_start_time) / 1000.0

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

    if state == STATE_PLAYING:
        all_dead = True
        for arrow in LEVELS[current_level]:
            if arrow.alive:
                all_dead = False
                break
        if all_dead and flying_arrow is None:
            state = STATE_RESULT
            result_message = "通关！"
            # 计算星级（用失误次数反推：初始 MAX_MISTAKES - 剩余）
            used_mistakes = MAX_MISTAKES - mistakes_left
            stars_earned = calculate_stars(elapsed_time, used_mistakes)

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