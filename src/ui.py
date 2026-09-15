import pygame
from src import config
from src import state


def cell_center(row, col):
    x = state.BOARD_LEFT + col * state.CELL_SIZE + state.CELL_SIZE // 2
    y = state.BOARD_TOP + row * state.CELL_SIZE + state.CELL_SIZE // 2
    return x, y


def draw_board(screen):
    for r in range(state.ROWS):
        for c in range(state.COLS):
            x = state.BOARD_LEFT + c * state.CELL_SIZE
            y = state.BOARD_TOP + r * state.CELL_SIZE
            rect = pygame.Rect(x + 2, y + 2, state.CELL_SIZE - 4, state.CELL_SIZE - 4)
            pygame.draw.rect(screen, config.CELL_BG_COLOR, rect, border_radius=8)


def draw_arrow(screen, cx, cy, direction, color):
    from src.game_data import UP, DOWN, LEFT, RIGHT
    size = int(state.CELL_SIZE * 0.5)

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
        pygame.draw.polygon(screen, config.ARROW_SHADOW, shadow_pts)

    pts = get_pts(0, 0)
    if pts:
        pygame.draw.polygon(screen, color, pts)


def get_result_buttons():
    if state.result_message == "游戏失败！":
        buttons = [("重新开始", "restart"), ("返回选关", "level_select"), ("返回主界面", "main_menu")]
    elif state.result_message == "通关！":
        buttons = [("重新开始", "restart"), ("下一关", "next"),
                   ("返回选关", "level_select"), ("返回主界面", "main_menu")]
    elif state.result_message == "恭喜完全通关！":
        buttons = [("重新开始", "restart"), ("返回选关", "level_select"), ("返回主界面", "main_menu")]
    else:
        buttons = [("重新开始", "restart")]

    btn_w = 150
    btn_h = 50
    gap = 20
    total_w = len(buttons) * btn_w + (len(buttons) - 1) * gap
    start_x = (config.WIDTH - total_w) // 2
    btn_y = config.HEIGHT // 2 + 60

    result = []
    for i, (label, action) in enumerate(buttons):
        rect = pygame.Rect(start_x + i * (btn_w + gap), btn_y, btn_w, btn_h)
        result.append((rect, label, action))
    return result


def draw_start_screen(screen, start_btn_rect):
    screen.fill(config.BG_COLOR)
    title = config.FONT_BIG.render("一箭又一箭", True, config.TEXT_COLOR)
    screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, 250))

    subtitle = config.FONT_SMALL.render("随机生成关卡 · 难度逐级提升", True, (120, 120, 120))
    screen.blit(subtitle, (config.WIDTH // 2 - subtitle.get_width() // 2, 340))

    mouse_pos = pygame.mouse.get_pos()
    color = config.BTN_HOVER if start_btn_rect.collidepoint(mouse_pos) else config.BTN_COLOR
    pygame.draw.rect(screen, color, start_btn_rect, border_radius=10)

    btn_text = config.FONT_MID.render("开始游戏", True, (255, 255, 255))
    screen.blit(btn_text, (start_btn_rect.centerx - btn_text.get_width() // 2,
                           start_btn_rect.centery - btn_text.get_height() // 2))


def draw_level_select_screen(screen, level_btn_rects, back_btn_rect, reset_btn_rect,
                             confirm_yes_rect, confirm_no_rect):
    screen.fill(config.BG_COLOR)

    title = config.FONT_BIG.render("选择关卡", True, config.TEXT_COLOR)
    screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, 40))

    mouse_pos = pygame.mouse.get_pos()
    for i in range(5):
        rect = level_btn_rects[i]
        unlocked = (i + 1) <= state.save_data["unlocked_level"]

        if not unlocked:
            color = config.BTN_LOCKED
        elif rect.collidepoint(mouse_pos):
            color = config.BTN_HOVER
        else:
            color = config.BTN_COLOR

        pygame.draw.rect(screen, color, rect, border_radius=10)

        level_text = config.FONT_MID.render(f"第 {i + 1} 关", True, (255, 255, 255))
        screen.blit(level_text, (rect.x + 20, rect.y + 10))

        if unlocked:
            stars = state.save_data["stars"][i]
            star_str = "★" * stars + "☆" * (3 - stars)
            star_text = config.FONT_SMALL.render(star_str, True, (255, 230, 100))
            screen.blit(star_text, (rect.x + 20, rect.y + 52))

            bt = state.save_data["best_times"][i]
            time_str = f"最快: {bt:.1f} 秒" if bt > 0 else "最快: --"
            time_text = config.FONT_TINY.render(time_str, True, (255, 255, 255))
            screen.blit(time_text, (rect.right - time_text.get_width() - 20, rect.y + 58))
        else:
            lock_text = config.FONT_SMALL.render("未解锁", True, (255, 255, 255))
            screen.blit(lock_text, (rect.right - lock_text.get_width() - 20, rect.y + 32))

    # 返回按钮
    color = config.BTN_HOVER if back_btn_rect.collidepoint(mouse_pos) else config.BTN_COLOR
    pygame.draw.rect(screen, color, back_btn_rect, border_radius=10)
    back_text = config.FONT_MID.render("返回", True, (255, 255, 255))
    screen.blit(back_text, (back_btn_rect.centerx - back_text.get_width() // 2,
                            back_btn_rect.centery - back_text.get_height() // 2))

    # 重置按钮
    color = config.BTN_DANGER_HOVER if reset_btn_rect.collidepoint(mouse_pos) else config.BTN_DANGER
    pygame.draw.rect(screen, color, reset_btn_rect, border_radius=10)
    reset_text = config.FONT_MID.render("重置记录", True, (255, 255, 255))
    screen.blit(reset_text, (reset_btn_rect.centerx - reset_text.get_width() // 2,
                             reset_btn_rect.centery - reset_text.get_height() // 2))

    # 确认弹窗
    if state.reset_confirm:
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        dialog = pygame.Rect(config.WIDTH // 2 - 220, config.HEIGHT // 2 - 110, 440, 220)
        pygame.draw.rect(screen, (255, 255, 255), dialog, border_radius=15)

        msg = config.FONT_MID.render("确定要重置所有记录吗？", True, config.TEXT_COLOR)
        screen.blit(msg, (config.WIDTH // 2 - msg.get_width() // 2, config.HEIGHT // 2 - 70))

        tip = config.FONT_TINY.render("解锁进度、星级和最快时间都将清零", True, (150, 150, 150))
        screen.blit(tip, (config.WIDTH // 2 - tip.get_width() // 2, config.HEIGHT // 2 - 30))

        color = config.BTN_DANGER_HOVER if confirm_yes_rect.collidepoint(mouse_pos) else config.BTN_DANGER
        pygame.draw.rect(screen, color, confirm_yes_rect, border_radius=8)
        yes_text = config.FONT_SMALL.render("确定", True, (255, 255, 255))
        screen.blit(yes_text, (confirm_yes_rect.centerx - yes_text.get_width() // 2,
                               confirm_yes_rect.centery - yes_text.get_height() // 2))

        color = config.BTN_HOVER if confirm_no_rect.collidepoint(mouse_pos) else config.BTN_COLOR
        pygame.draw.rect(screen, color, confirm_no_rect, border_radius=8)
        no_text = config.FONT_SMALL.render("取消", True, (255, 255, 255))
        screen.blit(no_text, (confirm_no_rect.centerx - no_text.get_width() // 2,
                              confirm_no_rect.centery - no_text.get_height() // 2))


def draw_playing_screen(screen, restart_btn_rect, undo_btn_rect):
    screen.fill(config.BG_COLOR)

    info = config.FONT_SMALL.render(f"第 {state.current_level + 1} 关", True, config.TEXT_COLOR)
    screen.blit(info, (20, 20))

    mistakes_text = config.FONT_SMALL.render(f"剩余失误: {state.mistakes_left}", True, config.TEXT_COLOR)
    screen.blit(mistakes_text, (20, 50))

    arrows_left = sum(1 for arrow in state.level_arrows if arrow.alive)
    arrows_text = config.FONT_SMALL.render(f"剩余箭头: {arrows_left}", True, config.TEXT_COLOR)
    screen.blit(arrows_text, (20, 80))

    time_text = config.FONT_SMALL.render(f"用时: {state.elapsed_time:.1f} 秒", True, config.TEXT_COLOR)
    screen.blit(time_text, (config.WIDTH - 180, 20))

    draw_board(screen)

    for arrow in state.level_arrows:
        if arrow.alive:
            if arrow is state.flying_arrow:
                draw_arrow(screen, state.flying_x, state.flying_y, arrow.direction, config.ARROW_COLOR)
            else:
                cx, cy = cell_center(arrow.row, arrow.col)
                if arrow is state.hit_arrow and state.hit_timer > 0:
                    draw_arrow(screen, cx, cy, arrow.direction, config.ARROW_HIT)
                elif arrow is state.selected_arrow:
                    draw_arrow(screen, cx, cy, arrow.direction, config.ARROW_SELECTED)
                else:
                    draw_arrow(screen, cx, cy, arrow.direction, config.ARROW_COLOR)

    mouse_pos = pygame.mouse.get_pos()

    btn_color = config.BTN_HOVER if restart_btn_rect.collidepoint(mouse_pos) else config.BTN_COLOR
    pygame.draw.rect(screen, btn_color, restart_btn_rect, border_radius=5)
    restart_text = config.FONT_SMALL.render("重新开始", True, (255, 255, 255))
    screen.blit(restart_text, (restart_btn_rect.centerx - restart_text.get_width() // 2,
                               restart_btn_rect.centery - restart_text.get_height() // 2))

    undo_color = config.BTN_HOVER if undo_btn_rect.collidepoint(mouse_pos) else config.BTN_COLOR
    if state.flying_arrow is not None or not state.history:
        undo_color = (180, 180, 180)
    pygame.draw.rect(screen, undo_color, undo_btn_rect, border_radius=5)
    undo_text = config.FONT_SMALL.render("撤销", True, (255, 255, 255))
    screen.blit(undo_text, (undo_btn_rect.centerx - undo_text.get_width() // 2,
                            undo_btn_rect.centery - undo_text.get_height() // 2))

    back = config.FONT_SMALL.render("按 ESC 返回选关", True, (120, 120, 120))
    screen.blit(back, (config.WIDTH // 2 - back.get_width() // 2, config.HEIGHT - 20))


def draw_result_screen(screen):
    screen.fill(config.BG_COLOR)

    if state.result_message == "通关！":
        tip = config.FONT_MID.render(f"通关！用时 {state.elapsed_time:.1f} 秒", True, config.TEXT_COLOR)
        screen.blit(tip, (config.WIDTH // 2 - tip.get_width() // 2, config.HEIGHT // 2 - 120))

        star_str = "★" * state.stars_earned + "☆" * (3 - state.stars_earned)
        star_text = config.FONT_BIG.render(star_str, True, (240, 180, 50))
        screen.blit(star_text, (config.WIDTH // 2 - star_text.get_width() // 2, config.HEIGHT // 2 - 70))
    elif state.result_message == "恭喜完全通关！":
        tip = config.FONT_MID.render("恭喜完全通关！", True, (240, 180, 50))
        screen.blit(tip, (config.WIDTH // 2 - tip.get_width() // 2, config.HEIGHT // 2 - 120))
        tip2 = config.FONT_SMALL.render("你已经征服了全部 5 个关卡！", True, config.TEXT_COLOR)
        screen.blit(tip2, (config.WIDTH // 2 - tip2.get_width() // 2, config.HEIGHT // 2 - 70))
    else:
        tip = config.FONT_MID.render("游戏失败！", True, config.TEXT_COLOR)
        screen.blit(tip, (config.WIDTH // 2 - tip.get_width() // 2, config.HEIGHT // 2 - 100))

    mouse_pos = pygame.mouse.get_pos()
    for rect, label, action in get_result_buttons():
        color = config.BTN_HOVER if rect.collidepoint(mouse_pos) else config.BTN_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=10)
        text = config.FONT_SMALL.render(label, True, (255, 255, 255))
        screen.blit(text, (rect.centerx - text.get_width() // 2,
                           rect.centery - text.get_height() // 2))