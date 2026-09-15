import pygame
from src import config
from src import state
from src.game_data import UP, DOWN, LEFT, RIGHT

# 渐变缓存（避免每帧重绘）
_gradients = {}


def load_backgrounds():
    """占位函数，保留接口兼容 main.py。现在不用图片了。"""
    pass


def _make_vertical_gradient(top_color, bottom_color):
    surf = pygame.Surface((config.WIDTH, config.HEIGHT))
    for y in range(config.HEIGHT):
        ratio = y / config.HEIGHT
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        pygame.draw.line(surf, (r, g, b), (0, y), (config.WIDTH, y))
    return surf


def get_gradient(key, top_color, bottom_color):
    if key not in _gradients:
        _gradients[key] = _make_vertical_gradient(top_color, bottom_color)
    return _gradients[key]


def draw_glow(screen, center, radius, color, max_alpha=70):
    """柔和的径向光晕"""
    glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for i in range(radius, 0, -3):
        alpha = int(max_alpha * (1 - i / radius))
        pygame.draw.circle(glow, (*color, alpha), (radius, radius), i)
    screen.blit(glow, (center[0] - radius, center[1] - radius))


def draw_soft_grid(screen, spacing, color, alpha=25):
    """淡淡的网格纹理"""
    layer = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
    for x in range(0, config.WIDTH, spacing):
        pygame.draw.line(layer, (*color, alpha), (x, 0), (x, config.HEIGHT), 1)
    for y in range(0, config.HEIGHT, spacing):
        pygame.draw.line(layer, (*color, alpha), (0, y), (config.WIDTH, y), 1)
    screen.blit(layer, (0, 0))


def draw_rounded_shadow(screen, rect, radius=12, offset=(3, 4), alpha=50):
    shadow = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, alpha),
                     (6, 6, rect.width, rect.height), border_radius=radius)
    screen.blit(shadow, (rect.x - 6 + offset[0] - 3, rect.y - 6 + offset[1] - 3))


def cell_center(row, col):
    x = state.BOARD_LEFT + col * state.CELL_SIZE + state.CELL_SIZE // 2
    y = state.BOARD_TOP + row * state.CELL_SIZE + state.CELL_SIZE // 2
    return x, y


def draw_button(screen, rect, text, font, base_color, hover_color,
                text_color=(255, 255, 255), radius=12):
    mouse_pos = pygame.mouse.get_pos()
    color = hover_color if rect.collidepoint(mouse_pos) else base_color

    # 阴影
    shadow = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 55), (4, 4, rect.width, rect.height),
                     border_radius=radius)
    screen.blit(shadow, (rect.x - 4, rect.y - 2))

    # 主体
    pygame.draw.rect(screen, color, rect, border_radius=radius)

    # 顶部高光（1px 白线，增加立体感）
    highlight = pygame.Surface((rect.width - 8, 2), pygame.SRCALPHA)
    highlight.fill((255, 255, 255, 60))
    screen.blit(highlight, (rect.x + 4, rect.y + 3))

    # 文字
    text_surf = font.render(text, True, text_color)
    screen.blit(text_surf, (rect.centerx - text_surf.get_width() // 2,
                            rect.centery - text_surf.get_height() // 2))


def draw_decor_arrow(screen, cx, cy, direction, size, color, alpha=60):
    """半透明装饰箭头"""
    layer = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    lcx, lcy = size, size
    if direction == RIGHT:
        pts = [(lcx + size // 2, lcy), (lcx - size // 2, lcy - size // 2),
               (lcx - size // 2, lcy + size // 2)]
    elif direction == LEFT:
        pts = [(lcx - size // 2, lcy), (lcx + size // 2, lcy - size // 2),
               (lcx + size // 2, lcy + size // 2)]
    elif direction == UP:
        pts = [(lcx, lcy - size // 2), (lcx - size // 2, lcy + size // 2),
               (lcx + size // 2, lcy + size // 2)]
    else:
        pts = [(lcx, lcy + size // 2), (lcx - size // 2, lcy - size // 2),
               (lcx + size // 2, lcy - size // 2)]
    pygame.draw.polygon(layer, (*color, alpha), pts)
    screen.blit(layer, (cx - size, cy - size))


def draw_board(screen):
    for r in range(state.ROWS):
        for c in range(state.COLS):
            x = state.BOARD_LEFT + c * state.CELL_SIZE
            y = state.BOARD_TOP + r * state.CELL_SIZE
            rect = pygame.Rect(x + 3, y + 3, state.CELL_SIZE - 6, state.CELL_SIZE - 6)
            # 格子阴影
            shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (100, 130, 170, 25), (0, 0, rect.width, rect.height),
                             border_radius=8)
            screen.blit(shadow, (rect.x + 1, rect.y + 2))
            # 格子
            pygame.draw.rect(screen, config.CELL_BG_COLOR, rect, border_radius=8)


def draw_arrow(screen, cx, cy, direction, color):
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

    shadow_pts = get_pts(2, 3)
    if shadow_pts:
        pygame.draw.polygon(screen, config.ARROW_SHADOW, shadow_pts)

    pts = get_pts(0, 0)
    if pts:
        pygame.draw.polygon(screen, color, pts)


def get_result_buttons():
    if state.result_message == "游戏失败！":
        buttons = [("重新开始", "restart"), ("返回选关", "level_select"),
                   ("返回主界面", "main_menu")]
    elif state.result_message == "通关！":
        buttons = [("重新开始", "restart"), ("下一关", "next"),
                   ("返回选关", "level_select"), ("返回主界面", "main_menu")]
    elif state.result_message == "恭喜完全通关！":
        buttons = [("重新开始", "restart"), ("返回选关", "level_select"),
                   ("返回主界面", "main_menu")]
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


# ============ 各个界面 ============

def draw_start_screen(screen, start_btn_rect):
    # 渐变背景：奶白 -> 淡蓝
    screen.blit(get_gradient("start", (250, 250, 247), (222, 233, 245)), (0, 0))

    # 中央柔光
    draw_glow(screen, (config.WIDTH // 2, 300), 280, (255, 255, 255), max_alpha=90)

    # 四角装饰箭头
    draw_decor_arrow(screen, 120, 160, RIGHT, 90, (140, 170, 210), 50)
    draw_decor_arrow(screen, 680, 160, LEFT, 90, (140, 170, 210), 50)
    draw_decor_arrow(screen, 120, 640, UP, 90, (140, 170, 210), 40)
    draw_decor_arrow(screen, 680, 640, UP, 90, (140, 170, 210), 40)

    # 标题（带阴影层）
    title_shadow = config.FONT_BIG.render("一箭又一箭", True, (190, 200, 215))
    screen.blit(title_shadow, (config.WIDTH // 2 - title_shadow.get_width() // 2 + 3, 273))
    title = config.FONT_BIG.render("一箭又一箭", True, (55, 80, 120))
    screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, 270))

    # 副标题
    subtitle = config.FONT_SMALL.render("随机生成关卡 · 难度逐级提升", True, (140, 155, 175))
    screen.blit(subtitle, (config.WIDTH // 2 - subtitle.get_width() // 2, 360))

    # 装饰性小横线
    pygame.draw.line(screen, (180, 195, 215),
                     (config.WIDTH // 2 - 60, 400), (config.WIDTH // 2 + 60, 400), 2)

    # 开始按钮
    draw_button(screen, start_btn_rect, "开始游戏", config.FONT_MID,
                config.BTN_COLOR, config.BTN_HOVER)


def draw_level_select_screen(screen, level_btn_rects, back_btn_rect, reset_btn_rect,
                             confirm_yes_rect, confirm_no_rect):
    # 渐变背景
    screen.blit(get_gradient("select", (245, 248, 252), (230, 238, 248)), (0, 0))

    # 淡淡网格
    draw_soft_grid(screen, 50, (150, 180, 220), alpha=18)

    title = config.FONT_BIG.render("选择关卡", True, (55, 80, 120))
    title_shadow = config.FONT_BIG.render("选择关卡", True, (200, 215, 235))
    screen.blit(title_shadow, (config.WIDTH // 2 - title_shadow.get_width() // 2 + 2, 42))
    screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, 40))

    mouse_pos = pygame.mouse.get_pos()
    for i in range(5):
        rect = level_btn_rects[i]
        unlocked = (i + 1) <= state.save_data["unlocked_level"]

        # 阴影
        draw_rounded_shadow(screen, rect, radius=14, offset=(2, 4), alpha=45)

        if not unlocked:
            color = config.BTN_LOCKED
        elif rect.collidepoint(mouse_pos):
            color = config.BTN_HOVER
        else:
            color = config.BTN_COLOR

        pygame.draw.rect(screen, color, rect, border_radius=14)

        # 左侧色条装饰（有锁的用灰色，解锁的用白色半透明）
        bar_color = (255, 255, 255, 100) if unlocked else (255, 255, 255, 60)
        bar = pygame.Surface((6, rect.height - 24), pygame.SRCALPHA)
        bar.fill(bar_color)
        screen.blit(bar, (rect.x + 10, rect.y + 12))

        level_text = config.FONT_MID.render(f"第 {i + 1} 关", True, (255, 255, 255))
        screen.blit(level_text, (rect.x + 28, rect.y + 12))

        if unlocked:
            stars = state.save_data["stars"][i]
            star_str = "★" * stars + "☆" * (3 - stars)
            star_text = config.FONT_SMALL.render(star_str, True, (255, 235, 120))
            screen.blit(star_text, (rect.x + 28, rect.y + 52))

            bt = state.save_data["best_times"][i]
            time_str = f"最快: {bt:.1f} 秒" if bt > 0 else "尚未通关"
            time_text = config.FONT_TINY.render(time_str, True, (255, 255, 255))
            screen.blit(time_text,
                        (rect.right - time_text.get_width() - 24, rect.y + 58))
        else:
            lock_text = config.FONT_SMALL.render("未解锁", True, (255, 255, 255))
            screen.blit(lock_text,
                        (rect.right - lock_text.get_width() - 24, rect.y + 32))

    draw_button(screen, back_btn_rect, "返回", config.FONT_MID,
                config.BTN_COLOR, config.BTN_HOVER)
    draw_button(screen, reset_btn_rect, "重置记录", config.FONT_MID,
                config.BTN_DANGER, config.BTN_DANGER_HOVER)

    if state.reset_confirm:
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        dialog = pygame.Rect(config.WIDTH // 2 - 220, config.HEIGHT // 2 - 110, 440, 220)
        draw_rounded_shadow(screen, dialog, radius=18, offset=(0, 6), alpha=80)
        pygame.draw.rect(screen, (255, 255, 255), dialog, border_radius=18)
        pygame.draw.rect(screen, (225, 230, 240), dialog, width=2, border_radius=18)

        msg = config.FONT_MID.render("确定要重置所有记录吗？", True, config.TEXT_COLOR)
        screen.blit(msg, (config.WIDTH // 2 - msg.get_width() // 2,
                          config.HEIGHT // 2 - 70))

        tip = config.FONT_TINY.render("解锁进度、星级和最快时间都将清零", True, (150, 150, 150))
        screen.blit(tip, (config.WIDTH // 2 - tip.get_width() // 2,
                          config.HEIGHT // 2 - 30))

        draw_button(screen, confirm_yes_rect, "确定", config.FONT_SMALL,
                    config.BTN_DANGER, config.BTN_DANGER_HOVER, radius=8)
        draw_button(screen, confirm_no_rect, "取消", config.FONT_SMALL,
                    config.BTN_COLOR, config.BTN_HOVER, radius=8)


def draw_playing_screen(screen, restart_btn_rect, undo_btn_rect):
    # 极浅渐变
    screen.blit(get_gradient("game", (245, 249, 253), (235, 243, 251)), (0, 0))

    # 中央光晕（棋盘区域更亮）
    draw_glow(screen, (config.WIDTH // 2, config.HEIGHT // 2 + 50),
              400, (255, 255, 255), max_alpha=55)

    # 顶部信息栏（半透明白条）
    top_bar = pygame.Surface((config.WIDTH, 110), pygame.SRCALPHA)
    top_bar.fill((255, 255, 255, 140))
    screen.blit(top_bar, (0, 0))

    info = config.FONT_SMALL.render(f"第 {state.current_level + 1} 关",
                                    True, (55, 80, 120))
    screen.blit(info, (24, 22))

    mistakes_text = config.FONT_SMALL.render(f"剩余失误: {state.mistakes_left}",
                                             True, config.TEXT_COLOR)
    screen.blit(mistakes_text, (24, 52))

    arrows_left = sum(1 for arrow in state.level_arrows if arrow.alive)
    arrows_text = config.FONT_SMALL.render(f"剩余箭头: {arrows_left}",
                                           True, config.TEXT_COLOR)
    screen.blit(arrows_text, (24, 82))

    time_text = config.FONT_SMALL.render(f"用时: {state.elapsed_time:.1f} 秒",
                                         True, (55, 80, 120))
    screen.blit(time_text, (config.WIDTH - time_text.get_width() - 24, 22))

    draw_board(screen)

    for arrow in state.level_arrows:
        if arrow.alive:
            if arrow is state.flying_arrow:
                draw_arrow(screen, state.flying_x, state.flying_y,
                           arrow.direction, config.ARROW_COLOR)
            else:
                cx, cy = cell_center(arrow.row, arrow.col)
                if arrow is state.hit_arrow and state.hit_timer > 0:
                    draw_arrow(screen, cx, cy, arrow.direction, config.ARROW_HIT)
                elif arrow is state.selected_arrow:
                    draw_arrow(screen, cx, cy, arrow.direction, config.ARROW_SELECTED)
                else:
                    draw_arrow(screen, cx, cy, arrow.direction, config.ARROW_COLOR)

    if state.flying_arrow is not None or not state.history:
        draw_button(screen, undo_btn_rect, "撤销", config.FONT_SMALL,
                    (200, 205, 215), (200, 205, 215), radius=8)
    else:
        draw_button(screen, undo_btn_rect, "撤销", config.FONT_SMALL,
                    config.BTN_COLOR, config.BTN_HOVER, radius=8)

    draw_button(screen, restart_btn_rect, "重新开始", config.FONT_SMALL,
                config.BTN_COLOR, config.BTN_HOVER, radius=8)

    back = config.FONT_SMALL.render("按 ESC 返回选关", True, (150, 165, 185))
    screen.blit(back, (config.WIDTH // 2 - back.get_width() // 2, config.HEIGHT - 24))


def draw_result_screen(screen):
    if state.result_message == "游戏失败！":
        screen.blit(get_gradient("lose", (235, 240, 248), (215, 225, 238)), (0, 0))
        draw_glow(screen, (config.WIDTH // 2, 300), 300, (255, 255, 255), max_alpha=50)
    else:
        screen.blit(get_gradient("win", (255, 250, 235), (248, 232, 200)), (0, 0))
        draw_glow(screen, (config.WIDTH // 2, 300), 320, (255, 240, 200), max_alpha=100)

        # 装饰星星
        draw_decor_arrow(screen, 140, 180, RIGHT, 50, (240, 200, 130), 60)
        draw_decor_arrow(screen, 660, 180, LEFT, 50, (240, 200, 130), 60)

    if state.result_message == "通关！":
        tip = config.FONT_MID.render(f"通关！用时 {state.elapsed_time:.1f} 秒",
                                     True, (80, 65, 40))
        screen.blit(tip, (config.WIDTH // 2 - tip.get_width() // 2,
                          config.HEIGHT // 2 - 130))

        star_str = "★" * state.stars_earned + "☆" * (3 - state.stars_earned)
        star_text = config.FONT_BIG.render(star_str, True, (230, 170, 50))
        screen.blit(star_text, (config.WIDTH // 2 - star_text.get_width() // 2,
                                config.HEIGHT // 2 - 80))
    elif state.result_message == "恭喜完全通关！":
        tip = config.FONT_MID.render("恭喜完全通关！", True, (200, 140, 40))
        screen.blit(tip, (config.WIDTH // 2 - tip.get_width() // 2,
                          config.HEIGHT // 2 - 130))
        tip2 = config.FONT_SMALL.render("你已经征服了全部 5 个关卡！",
                                        True, (120, 100, 70))
        screen.blit(tip2, (config.WIDTH // 2 - tip2.get_width() // 2,
                           config.HEIGHT // 2 - 80))
    else:
        tip = config.FONT_MID.render("游戏失败！", True, (70, 85, 110))
        screen.blit(tip, (config.WIDTH // 2 - tip.get_width() // 2,
                          config.HEIGHT // 2 - 110))

    for rect, label, action in get_result_buttons():
        draw_button(screen, rect, label, config.FONT_SMALL,
                    config.BTN_COLOR, config.BTN_HOVER)