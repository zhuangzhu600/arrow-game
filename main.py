import pygame
import sys
import random

from src import config
from src import state
from src import ui
from src.game_data import can_fly_out, generate_random_level
from src.save_system import load_save, write_save, get_default_save

pygame.init()
screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
pygame.display.set_caption("一箭又一箭")
clock = pygame.time.Clock()
config.init_fonts()

state.save_data = load_save()

# 按钮区域
start_btn_rect = pygame.Rect(config.WIDTH // 2 - 100, 500, 200, 60)
restart_btn_rect = pygame.Rect(20, config.HEIGHT - 60, 120, 40)
undo_btn_rect = pygame.Rect(config.WIDTH - 140, config.HEIGHT - 60, 120, 40)
back_btn_rect = pygame.Rect(config.WIDTH // 2 - 180, config.HEIGHT - 100, 160, 50)
reset_btn_rect = pygame.Rect(config.WIDTH // 2 + 20, config.HEIGHT - 100, 160, 50)
confirm_yes_rect = pygame.Rect(config.WIDTH // 2 - 110, config.HEIGHT // 2 + 20, 100, 50)
confirm_no_rect = pygame.Rect(config.WIDTH // 2 + 10, config.HEIGHT // 2 + 20, 100, 50)

level_btn_rects = []
for i in range(5):
    y = 140 + i * 105
    level_btn_rects.append(pygame.Rect(config.WIDTH // 2 - 220, y, 440, 90))


def update_board_layout():
    max_board_size = 600
    state.CELL_SIZE = min(max_board_size // state.COLS, max_board_size // state.ROWS)
    state.BOARD_LEFT = (config.WIDTH - state.COLS * state.CELL_SIZE) // 2
    state.BOARD_TOP = 100 + (max_board_size - state.ROWS * state.CELL_SIZE) // 2


def load_level(level_index):
    rows, cols, min_arrows, max_arrows = config.LEVEL_CONFIGS[level_index]
    state.ROWS = rows
    state.COLS = cols
    update_board_layout()
    num_arrows = random.randint(min_arrows, max_arrows)
    state.level_arrows = generate_random_level(state.ROWS, state.COLS, num_arrows)
    state.current_level = level_index


def pos_to_cell(pos):
    x, y = pos
    if x < state.BOARD_LEFT or x >= state.BOARD_LEFT + state.COLS * state.CELL_SIZE:
        return None
    if y < state.BOARD_TOP or y >= state.BOARD_TOP + state.ROWS * state.CELL_SIZE:
        return None
    col = (x - state.BOARD_LEFT) // state.CELL_SIZE
    row = (y - state.BOARD_TOP) // state.CELL_SIZE
    return int(row), int(col)


def find_arrow_at(row, col):
    for arrow in state.level_arrows:
        if arrow.alive and arrow.row == row and arrow.col == col:
            return arrow
    return None


def reset_level():
    state.mistakes_left = config.MAX_MISTAKES
    state.selected_arrow = None
    state.hit_arrow = None
    state.hit_timer = 0
    state.flying_arrow = None
    state.history = []
    state.elapsed_time = 0.0
    state.stars_earned = 0
    state.level_start_time = pygame.time.get_ticks()
    for arrow in state.level_arrows:
        arrow.alive = True


def calculate_stars(time_used, mistakes_used):
    if time_used <= 20 and mistakes_used == 0:
        return 3
    elif time_used <= 40 and mistakes_used <= 1:
        return 2
    else:
        return 1


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if state.mode == config.STATE_PLAYING:
                    state.mode = config.STATE_LEVEL_SELECT
                    state.selected_arrow = None
                    state.hit_arrow = None
                    state.hit_timer = 0
                    state.flying_arrow = None
                    state.history = []
                elif state.mode == config.STATE_LEVEL_SELECT:
                    if state.reset_confirm:
                        state.reset_confirm = False
                    else:
                        state.mode = config.STATE_START
                elif state.mode == config.STATE_RESULT:
                    state.mode = config.STATE_LEVEL_SELECT
                    reset_level()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state.mode == config.STATE_START:
                if start_btn_rect.collidepoint(event.pos):
                    state.mode = config.STATE_LEVEL_SELECT

            elif state.mode == config.STATE_LEVEL_SELECT:
                if state.reset_confirm:
                    if confirm_yes_rect.collidepoint(event.pos):
                        state.save_data = get_default_save()
                        write_save(state.save_data)
                        state.reset_confirm = False
                    elif confirm_no_rect.collidepoint(event.pos):
                        state.reset_confirm = False
                else:
                    if back_btn_rect.collidepoint(event.pos):
                        state.mode = config.STATE_START
                    elif reset_btn_rect.collidepoint(event.pos):
                        state.reset_confirm = True
                    else:
                        for i in range(5):
                            if level_btn_rects[i].collidepoint(event.pos):
                                if (i + 1) <= state.save_data["unlocked_level"]:
                                    load_level(i)
                                    reset_level()
                                    state.mode = config.STATE_PLAYING
                                break

            elif state.mode == config.STATE_PLAYING:
                if restart_btn_rect.collidepoint(event.pos):
                    reset_level()
                elif undo_btn_rect.collidepoint(event.pos):
                    if state.flying_arrow is None and state.history:
                        action_type, arrow = state.history.pop()
                        if action_type == 'fly':
                            arrow.alive = True
                        elif action_type == 'hit':
                            state.mistakes_left += 1
                elif state.flying_arrow is None:
                    cell = pos_to_cell(event.pos)
                    if cell:
                        row, col = cell
                        arrow = find_arrow_at(row, col)
                        if arrow:
                            state.selected_arrow = arrow
                            if can_fly_out(arrow, state.level_arrows, state.ROWS, state.COLS):
                                state.flying_arrow = arrow
                                state.flying_x, state.flying_y = ui.cell_center(arrow.row, arrow.col)
                                state.selected_arrow = None
                                state.history.append(('fly', arrow))
                            else:
                                state.hit_arrow = arrow
                                state.hit_timer = 20
                                state.mistakes_left -= 1
                                state.history.append(('hit', None))
                                if state.mistakes_left <= 0:
                                    state.mode = config.STATE_RESULT
                                    state.result_message = "游戏失败！"
                                    state.selected_arrow = None
                        else:
                            state.selected_arrow = None

            elif state.mode == config.STATE_RESULT:
                for rect, label, action in ui.get_result_buttons():
                    if rect.collidepoint(event.pos):
                        if action == "restart":
                            reset_level()
                            state.mode = config.STATE_PLAYING
                        elif action == "next":
                            if state.current_level + 1 < len(config.LEVEL_CONFIGS):
                                load_level(state.current_level + 1)
                                reset_level()
                                state.mode = config.STATE_PLAYING
                        elif action == "level_select":
                            reset_level()
                            state.mode = config.STATE_LEVEL_SELECT
                        elif action == "main_menu":
                            reset_level()
                            state.mode = config.STATE_START
                        break

    if state.mode == config.STATE_PLAYING:
        state.elapsed_time = (pygame.time.get_ticks() - state.level_start_time) / 1000.0

    if state.flying_arrow is not None:
        dr, dc = state.flying_arrow.direction
        state.flying_x += dc * state.flying_speed
        state.flying_y += dr * state.flying_speed

        if (state.flying_x < state.BOARD_LEFT - state.CELL_SIZE or
            state.flying_x > state.BOARD_LEFT + state.COLS * state.CELL_SIZE + state.CELL_SIZE or
            state.flying_y < state.BOARD_TOP - state.CELL_SIZE or
            state.flying_y > state.BOARD_TOP + state.ROWS * state.CELL_SIZE + state.CELL_SIZE):
            state.flying_arrow.alive = False
            state.flying_arrow = None

    if state.mode == config.STATE_PLAYING:
        all_dead = True
        for arrow in state.level_arrows:
            if arrow.alive:
                all_dead = False
                break
        if all_dead and state.flying_arrow is None:
            state.mode = config.STATE_RESULT
            used_mistakes = config.MAX_MISTAKES - state.mistakes_left
            state.stars_earned = calculate_stars(state.elapsed_time, used_mistakes)

            if state.stars_earned > state.save_data["stars"][state.current_level]:
                state.save_data["stars"][state.current_level] = state.stars_earned
            bt = state.save_data["best_times"][state.current_level]
            if bt == 0 or state.elapsed_time < bt:
                state.save_data["best_times"][state.current_level] = state.elapsed_time
            if state.current_level + 1 < len(config.LEVEL_CONFIGS):
                if state.save_data["unlocked_level"] < state.current_level + 2:
                    state.save_data["unlocked_level"] = state.current_level + 2
            write_save(state.save_data)

            if state.current_level >= len(config.LEVEL_CONFIGS) - 1:
                state.result_message = "恭喜完全通关！"
            else:
                state.result_message = "通关！"

    if state.mode == config.STATE_START:
        ui.draw_start_screen(screen, start_btn_rect)
    elif state.mode == config.STATE_LEVEL_SELECT:
        ui.draw_level_select_screen(screen, level_btn_rects, back_btn_rect, reset_btn_rect,
                                    confirm_yes_rect, confirm_no_rect)
    elif state.mode == config.STATE_PLAYING:
        ui.draw_playing_screen(screen, restart_btn_rect, undo_btn_rect)
    elif state.mode == config.STATE_RESULT:
        ui.draw_result_screen(screen)

    if state.hit_timer > 0:
        state.hit_timer -= 1
    else:
        state.hit_arrow = None

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()