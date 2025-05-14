import pygame
from pathlib import Path

import fantas
from fantas import uimanager as u

import Display.color as color
import Display.textstyle as textstyle


def show_start_window(ms):
    u.init((768, 480), r=1, flags=pygame.SRCALPHA | pygame.HWSURFACE | pygame.NOFRAME)
    u.root = fantas.Root(color.FAKEWHITE)
    images = fantas.load_res_group(Path('res/image/').iterdir())
    fonts = fantas.load_res_group(Path('res/font/').iterdir())

    img = fantas.Ui(
        pygame.transform.smoothscale(images["启动背景"], u.size),
        topleft=(0, -100))
    img.size = u.size
    img.join(u.root)

    border = fantas.Label(u.size, bd=4, sc=color.FAKEWHITE)
    border.join(u.root)
    
    bottom_box = fantas.Label((u.WIDTH - border.bd * 2, 200), bg = color.FAKEWHITE, bottomleft=(border.bd, u.HEIGHT - border.bd))
    bottom_box.join(u.root)

    icon = fantas.Ui(images['icon'], center=(bottom_box.rect.h / 2, bottom_box.rect.top + bottom_box.rect.h / 2))
    icon.size = (128, 128)
    icon.join(u.root)

<<<<<<< HEAD
    main_title = fantas.Text("三独立节点电路通用 - 正弦稳态分析器", fonts['shuhei'], textstyle.DARKBLUE_TITLE_3, midleft=(bottom_box.rect.h, bottom_box.rect.top + bottom_box.rect.h / 4))
=======
    main_title = fantas.Text("三独立节点电路 - 正弦稳态分析器", fonts['shuhei'], textstyle.DARKBLUE_TITLE_3, midleft=(bottom_box.rect.h, bottom_box.rect.top + bottom_box.rect.h / 4))
>>>>>>> 39c291a (初步搭建界面)
    main_title.join(u.root)

    sub_title = fantas.Text("山东大学 2024-2025 学年 24级 电路课程设计作业", fonts['shuhei'], textstyle.DARKBLUE_TITLE_5, midleft=(bottom_box.rect.h, bottom_box.rect.top + bottom_box.rect.h / 2))
    sub_title.join(u.root)

    def quit():
        pygame.time.set_timer(pygame.QUIT, 0)
        pygame.display.quit()
        pygame.display.init()
    
    pygame.time.set_timer(pygame.QUIT, ms, 1)
    u.mainloop(quit)
<<<<<<< HEAD
from Core.Component import node_0, node_1, node_2, node_3
=======
>>>>>>> 39c291a (初步搭建界面)
