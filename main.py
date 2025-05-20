import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ''

import pygame
from pathlib import Path

import fantas
from fantas import uimanager as u

settings_path = Path(".settings")
u.settings = fantas.load(settings_path)


import Display.color as color
# import Display.textstyle as textstyle
# import Display.buttonstyle as buttonstyle

import Display.launch as launch
launch.show_start_window(2500)    # 启动窗口

info = pygame.display.Info()
if info.current_w == 1920 and info.current_h == 1080:
    u.init((1920, 1080), r=1, flags=pygame.SRCALPHA | pygame.HWSURFACE | pygame.FULLSCREEN)
else:
    u.init((1920, 1080), r=1, flags=pygame.SRCALPHA | pygame.HWSURFACE)
u.images = fantas.load_res_group(Path('res/image/').iterdir())
u.fonts = fantas.load_res_group(Path('res/font/').iterdir())

pygame.display.set_caption('电路分析器')
pygame.display.set_icon(u.images['icon'])

u.root = fantas.Root(color.FAKEWHITE)

import Display.viewbox as viewbox
import Display.sidebar as sidebar

viewbox.layout()
sidebar.layout()

def quit():
    import sys
    fantas.dump(u.settings, settings_path)
    pygame.quit()
    sys.exit()

u.mainloop(quit)
