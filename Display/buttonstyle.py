import pygame
import Display.color as color

offset = pygame.Color(50, 50, 50, 0)

common_button_style = {
    'origin_bg': color.LIGHTWHITE,
    'origin_sc': color.GRAY,
    'origin_bd': 2,

    'hover_bg': color.GRAY,
    'hover_sc': color.GRAY,
    'hover_bd': 2,

    'press_bg': color.GRAY - offset,
    'press_sc': color.GRAY,
    'press_bd': 2,
}

del pygame, offset, color
