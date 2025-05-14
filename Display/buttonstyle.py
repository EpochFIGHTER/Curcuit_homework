import pygame
from Display.color import *

offset = pygame.Color(50, 50, 50, 0)

edit_name_button_style = {
    'origin_bg': LIGHTWHITE,
    'origin_sc': GRAY,
    'origin_bd': 2,

    'hover_bg': GRAY,
    'hover_sc': GRAY,
    'hover_bd': 2,

    'press_bg': GRAY - offset,
    'press_sc': GRAY,
    'press_bd': 2,
}


del pygame, offset
