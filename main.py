import pygame
import sys

# 初始化 pygame
pygame.init()

# 设置窗口大小
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")

# 游戏主循环
running = True
while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 填充背景色（浅灰色）
    screen.fill((240, 240, 240))

    # 刷新屏幕
    pygame.display.flip()

# 退出游戏
pygame.quit()
sys.exit()