import pygame
import sys
import json
import os
import random

from game_data import *

pygame.init()

WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")
clock = pygame.time.Clock()

# 颜色
BG_COLOR = (240, 240, 240)
TEXT_COLOR = (50, 50, 50)
BTN_COLOR = (100, 160, 220)
BTN_HOVER = (70, 130, 200)
BTN_LOCKED = (190, 190, 190)
ARROW_COLOR = (60, 90, 140)
ARROW_SELECTED = (230, 120, 60)
ARROW_HIT = (220, 60, 60)
CELL_BG_COLOR = (225, 235, 245)
ARROW_SHADOW = (200, 200, 200)

# 字体
FONT_BIG = pygame.font.SysFont("simhei", 48)
FONT_MID = pygame.font.SysFont("simhei", 28)
FONT_SMALL = pygame.font.SysFont("simhei", 22)
FONT_TINY = pygame.font.SysFont("simhei", 18)

# 5 个关卡的难度配置
# (行, 列, 最少箭头, 最多箭头)
LEVEL_CONFIGS = [
    (5, 5, 6, 8),
    (6, 6, 9, 12),
    (7, 7, 13, 16),
    (8, 8, 17, 21),
    (9, 9, 21, 26),
]

# 存档文件
SAVE_FILE = "save.json"


def load_save():
    default = {
        "unlocked_level": 1,
        "stars": [0, 0, 0, 0, 0],
        "best_times": [0.0, 0.0, 0.0, 0.0, 0.0],
    }
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key in default:
                    if key not in data:
                        data[key] = default[key]
                return data
        except Exception:
            pass
    return default


def write_save(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


save_data = load_save()

# 动态棋盘参数
ROWS = 5
COLS = 5
CELL_SIZE = 90
BOARD_LEFT = 0
BOARD_TOP = 0

# 游戏状态
STATE_START = "start"
STATE_LEVEL_SELECT = "level_select"
STATE_PLAYING = "playing"
STATE_RESULT = "result"
state = STATE_START

current_level = 0
level_arrows = []

selected_arrow = None
hit_arrow = None
hit_timer = 0
result_message = ""

mistakes_left = MAX_MISTAKES
flying_arrow = None
flying_x = 0
flying_y = 0
flying_speed = 12

level_start_time = 0
elapsed_time = 0.0
stars_earned = 0

history = []

# 按钮区域
start_btn_rect = pygame.Rect(WIDTH // 2 - 100, 500, 200, 60)
restart_btn_rect = pygame.Rect(20, HEIGHT - 60, 120, 40)
undo_btn_rect = pygame.Rect(WIDTH - 140, HEIGHT - 60, 120, 40)
back_btn_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT - 100, 160, 50)

level_btn_rects = []
for i in range(5):
    y = 140 + i * 105
    level_btn_rects.append(pygame.Rect(WIDTH // 2 - 220, y, 440, 90))


def get_result_buttons():
    """根据当前结果状态，动态返回居中排列的按钮列表"""
    if result_message == "游戏失败！":
        buttons = [("重新开始", "restart"), ("返回选关", "level_select"), ("返回主界面", "main_menu")]
    elif result_message == "通关！":
        buttons = [("重新开始", "restart"), ("下一关", "next"),
                   ("返回选关", "level_select"), ("返回主界面", "main_menu")]
    elif result_message == "恭喜完全通关！":
        buttons = [("重新开始", "restart"), ("返回选关", "level_select"), ("返回主界面", "main_menu")]
    else:
        buttons = [("重新开始", "restart")]

    btn_w = 150
    btn_h = 50
    gap = 20
    total_w = len(buttons) * btn_w + (len(buttons) - 1) * gap
    start_x = (WIDTH - total_w) // 2
    btn_y = HEIGHT // 2 + 60

    result = []
    for i, (label, action) in enumerate(buttons):
        rect = pygame.Rect(start_x + i * (btn_w + gap), btn_y, btn_w, btn_h)
        result.append((rect, label, action))
    return result


def update_board_layout():
    global CELL_SIZE, BOARD_LEFT, BOARD_TOP
    max_board_size = 600
    CELL_SIZE = min(max_board_size // COLS, max_board_size // ROWS)
    BOARD_LEFT = (WIDTH - COLS * CELL_SIZE) // 2
    BOARD_TOP = 100 + (max_board_size - ROWS * CELL_SIZE) // 2


def load_level(level_index):
    global ROWS, COLS, level_arrows, current_level
    rows, cols, min_arrows, max_arrows = LEVEL_CONFIGS[level_index]
    ROWS = rows
    COLS = cols
    update_board_layout()
    # 箭头数量在区间内随机，盘面真随机（不传 seed）
    num_arrows = random.randint(min_arrows, max_arrows)
    level_arrows = generate_random_level(ROWS, COLS, num_arrows)
    current_level = level_index


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
    for arrow in level_arrows:
        if arrow.alive and arrow.row == row and arrow.col == col:
            return arrow
    return None


def draw_board():
    for r in range(ROWS):
        for c in range(COLS):
            x = BOARD_LEFT + c * CELL_SIZE
            y = BOARD_TOP + r * CELL_SIZE
            rect = pygame.Rect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
            pygame.draw.rect(screen, CELL_BG_COLOR, rect, border_radius=8)


def draw_arrow(cx, cy, direction, color):
    size = int(CELL_SIZE * 0.5)

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

    shadow_pts = get_pts(2, 2)
    if shadow_pts:
        pygame.draw.polygon(screen, ARROW_SHADOW, shadow_pts)

    pts = get_pts(0, 0)
    if pts:
        pygame.draw.polygon(screen, color, pts)


def draw_start_screen():
    screen.fill(BG_COLOR)
    title = FONT_BIG.render("一箭又一箭", True, TEXT_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 250))

    subtitle = FONT_SMALL.render("随机生成关卡 · 难度逐级提升", True, (120, 120, 120))
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 340))

    mouse_pos = pygame.mouse.get_pos()
    color = BTN_HOVER if start_btn_rect.collidepoint(mouse_pos) else BTN_COLOR
    pygame.draw.rect(screen, color, start_btn_rect, border_radius=10)

    btn_text = FONT_MID.render("开始游戏", True, (255, 255, 255))
    screen.blit(btn_text, (start_btn_rect.centerx - btn_text.get_width() // 2,
                           start_btn_rect.centery - btn_text.get_height() // 2))


def draw_level_select_screen():
    screen.fill(BG_COLOR)

    title = FONT_BIG.render("选择关卡", True, TEXT_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

    mouse_pos = pygame.mouse.get_pos()
    for i in range(5):
        rect = level_btn_rects[i]
        unlocked = (i + 1) <= save_data["unlocked_level"]

        if not unlocked:
            color = BTN_LOCKED
        elif rect.collidepoint(mouse_pos):
            color = BTN_HOVER
        else:
            color = BTN_COLOR

        pygame.draw.rect(screen, color, rect, border_radius=10)

        level_text = FONT_MID.render(f"第 {i + 1} 关", True, (255, 255, 255))
        screen.blit(level_text, (rect.x + 20, rect.y + 10))

        if unlocked:
            stars = save_data["stars"][i]
            star_str = "★" * stars + "☆" * (3 - stars)
            star_text = FONT_SMALL.render(star_str, True, (255, 230, 100))
            screen.blit(star_text, (rect.x + 20, rect.y + 52))

            bt = save_data["best_times"][i]
            if bt > 0:
                time_str = f"最快: {bt:.1f} 秒"
            else:
                time_str = "最快: --"
            time_text = FONT_TINY.render(time_str, True, (255, 255, 255))
            screen.blit(time_text, (rect.right - time_text.get_width() - 20, rect.y + 58))
        else:
            lock_text = FONT_SMALL.render("未解锁", True, (255, 255, 255))
            screen.blit(lock_text, (rect.right - lock_text.get_width() - 20, rect.y + 32))

    color = BTN_HOVER if back_btn_rect.collidepoint(mouse_pos) else BTN_COLOR
    pygame.draw.rect(screen, color, back_btn_rect, border_radius=10)
    back_text = FONT_MID.render("返回", True, (255, 255, 255))
    screen.blit(back_text, (back_btn_rect.centerx - back_text.get_width() // 2,
                            back_btn_rect.centery - back_text.get_height() // 2))


def draw_playing_screen():
    screen.fill(BG_COLOR)

    info = FONT_SMALL.render(f"第 {current_level + 1} 关", True, TEXT_COLOR)
    screen.blit(info, (20, 20))

    mistakes_text = FONT_SMALL.render(f"剩余失误: {mistakes_left}", True, TEXT_COLOR)
    screen.blit(mistakes_text, (20, 50))

    arrows_left = sum(1 for arrow in level_arrows if arrow.alive)
    arrows_text = FONT_SMALL.render(f"剩余箭头: {arrows_left}", True, TEXT_COLOR)
    screen.blit(arrows_text, (20, 80))

    time_text = FONT_SMALL.render(f"用时: {elapsed_time:.1f} 秒", True, TEXT_COLOR)
    screen.blit(time_text, (WIDTH - 180, 20))

    draw_board()

    for arrow in level_arrows:
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

    back = FONT_SMALL.render("按 ESC 返回选关", True, (120, 120, 120))
    screen.blit(back, (WIDTH // 2 - back.get_width() // 2, HEIGHT - 20))


def draw_result_screen():
    screen.fill(BG_COLOR)

    if result_message == "通关！":
        tip = FONT_MID.render(f"通关！用时 {elapsed_time:.1f} 秒", True, TEXT_COLOR)
        screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 2 - 120))

        star_str = "★" * stars_earned + "☆" * (3 - stars_earned)
        star_text = FONT_BIG.render(star_str, True, (240, 180, 50))
        screen.blit(star_text, (WIDTH // 2 - star_text.get_width() // 2, HEIGHT // 2 - 70))
    elif result_message == "恭喜完全通关！":
        tip = FONT_MID.render("恭喜完全通关！", True, (240, 180, 50))
        screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 2 - 120))
        tip2 = FONT_SMALL.render("你已经征服了全部 5 个关卡！", True, TEXT_COLOR)
        screen.blit(tip2, (WIDTH // 2 - tip2.get_width() // 2, HEIGHT // 2 - 70))
    else:
        tip = FONT_MID.render("游戏失败！", True, TEXT_COLOR)
        screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 2 - 100))

    # 动态绘制居中排列的按钮
    mouse_pos = pygame.mouse.get_pos()
    for rect, label, action in get_result_buttons():
        color = BTN_HOVER if rect.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=10)
        text = FONT_SMALL.render(label, True, (255, 255, 255))
        screen.blit(text, (rect.centerx - text.get_width() // 2,
                           rect.centery - text.get_height() // 2))


def calculate_stars(time_used, mistakes_used):
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
    level_start_time = pygame.time.get_ticks()
    for arrow in level_arrows:
        arrow.alive = True


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if state == STATE_PLAYING:
                    state = STATE_LEVEL_SELECT
                    selected_arrow = None
                    hit_arrow = None
                    hit_timer = 0
                    flying_arrow = None
                    history = []
                elif state == STATE_LEVEL_SELECT:
                    state = STATE_START
                elif state == STATE_RESULT:
                    state = STATE_LEVEL_SELECT
                    reset_level()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == STATE_START:
                if start_btn_rect.collidepoint(event.pos):
                    state = STATE_LEVEL_SELECT

            elif state == STATE_LEVEL_SELECT:
                if back_btn_rect.collidepoint(event.pos):
                    state = STATE_START
                else:
                    for i in range(5):
                        if level_btn_rects[i].collidepoint(event.pos):
                            if (i + 1) <= save_data["unlocked_level"]:
                                load_level(i)
                                reset_level()
                                state = STATE_PLAYING
                            break

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
                            if can_fly_out(arrow, level_arrows, ROWS, COLS):
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
                for rect, label, action in get_result_buttons():
                    if rect.collidepoint(event.pos):
                        if action == "restart":
                            reset_level()
                            state = STATE_PLAYING
                        elif action == "next":
                            if current_level + 1 < len(LEVEL_CONFIGS):
                                load_level(current_level + 1)
                                reset_level()
                                state = STATE_PLAYING
                        elif action == "level_select":
                            reset_level()
                            state = STATE_LEVEL_SELECT
                        elif action == "main_menu":
                            reset_level()
                            state = STATE_START
                        break

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
        for arrow in level_arrows:
            if arrow.alive:
                all_dead = False
                break
        if all_dead and flying_arrow is None:
            state = STATE_RESULT
            used_mistakes = MAX_MISTAKES - mistakes_left
            stars_earned = calculate_stars(elapsed_time, used_mistakes)

            if stars_earned > save_data["stars"][current_level]:
                save_data["stars"][current_level] = stars_earned
            bt = save_data["best_times"][current_level]
            if bt == 0 or elapsed_time < bt:
                save_data["best_times"][current_level] = elapsed_time
            if current_level + 1 < len(LEVEL_CONFIGS):
                if save_data["unlocked_level"] < current_level + 2:
                    save_data["unlocked_level"] = current_level + 2
            write_save(save_data)

            if current_level >= len(LEVEL_CONFIGS) - 1:
                result_message = "恭喜完全通关！"
            else:
                result_message = "通关！"

    if state == STATE_START:
        draw_start_screen()
    elif state == STATE_LEVEL_SELECT:
        draw_level_select_screen()
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