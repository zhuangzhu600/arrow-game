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

# 字体（用系统自带字体，支持中文）
FONT_BIG = pygame.font.SysFont("simhei", 48)
FONT_MID = pygame.font.SysFont("simhei", 28)
FONT_SMALL = pygame.font.SysFont("simhei", 22)

# 游戏状态：start / playing / result
STATE_START = "start"
STATE_PLAYING = "playing"
STATE_RESULT = "result"
state = STATE_START

# 开始按钮区域
start_btn_rect = pygame.Rect(WIDTH // 2 - 100, 350, 200, 60)


def draw_start_screen():
    """画开始界面"""
    screen.fill(BG_COLOR)
    title = FONT_BIG.render("一箭又一箭", True, TEXT_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 180))

    # 根据鼠标是否悬停在按钮上，换颜色
    mouse_pos = pygame.mouse.get_pos()
    color = BTN_HOVER if start_btn_rect.collidepoint(mouse_pos) else BTN_COLOR
    pygame.draw.rect(screen, color, start_btn_rect, border_radius=10)

    btn_text = FONT_MID.render("开始游戏", True, (255, 255, 255))
    screen.blit(
        btn_text,
        (
            start_btn_rect.centerx - btn_text.get_width() // 2,
            start_btn_rect.centery - btn_text.get_height() // 2,
        ),
    )


def draw_playing_screen():
    """画游戏界面（暂时先放个占位文字）"""
    screen.fill(BG_COLOR)
    tip = FONT_MID.render("游戏界面（待开发）", True, TEXT_COLOR)
    screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 2 - 20))

    back = FONT_SMALL.render("按 ESC 返回开始界面", True, (120, 120, 120))
    screen.blit(back, (WIDTH // 2 - back.get_width() // 2, HEIGHT - 60))


def draw_result_screen():
    """画结果界面（暂时先放个占位文字）"""
    screen.fill(BG_COLOR)
    tip = FONT_MID.render("结果界面（待开发）", True, TEXT_COLOR)
    screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 2 - 20))


# 游戏主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 键盘事件
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and state == STATE_PLAYING:
                state = STATE_START

        # 鼠标点击事件
        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == STATE_START:
                if start_btn_rect.collidepoint(event.pos):
                    state = STATE_PLAYING

    # 根据状态画不同界面
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