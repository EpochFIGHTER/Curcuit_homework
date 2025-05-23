import pygame
from fantas import uimanager as u
import Display.color as color

IS_DARKMODE = False
BLACK       = pygame.Color("#000000")
WHITE       = pygame.Color("#ffffff")
FAKEWHITE   = pygame.Color("#e3e3e3")
DARKBLUE    = pygame.Color("#003658")
LIGHTWHITE  = pygame.Color("#faf7ff")
DEEPWHITE   = pygame.Color("#c4c7cc")
THEMEBLUE   = pygame.Color("#8685ef")
GRAY        = pygame.Color("#aca9bb")
LIGHTGREEN  = pygame.Color("#c5ebde")
RED         = pygame.Color("#fa575d")
LIGHTBLUE   = pygame.Color("#c6c0f8")

# 反色
def flip_color(color):
    c = WHITE - color
    c.a = 255
    return c

# 切换颜色模式
def switch_dark_mode():
    global IS_DARKMODE, u
    u.settings['DARK_MODE'] = IS_DARKMODE = not IS_DARKMODE
    color.BLACK       = flip_color(color.BLACK)
    color.FAKEWHITE   = flip_color(color.FAKEWHITE)
    color.DARKBLUE    = flip_color(color.DARKBLUE)
    color.LIGHTWHITE  = flip_color(color.LIGHTWHITE)
    color.DEEPWHITE   = flip_color(color.DEEPWHITE)
    color.THEMEBLUE   = flip_color(color.THEMEBLUE)
    color.GRAY        = flip_color(color.GRAY)
    color.LIGHTGREEN  = flip_color(color.LIGHTGREEN)
    color.RED         = flip_color(color.RED)
    color.LIGHTBLUE   = flip_color(color.LIGHTBLUE)

if u.settings['DARK_MODE']:
    switch_dark_mode()

del pygame
