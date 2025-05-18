import pygame
import Display.color as color

offset_large = pygame.Color(50, 50, 50, 0)
offset_small = pygame.Color(30, 30, 30, 0)

common_button_style = {
    'origin_bg': color.LIGHTWHITE,
    'origin_sc': color.GRAY,
    'origin_bd': 2,

    'hover_bg': color.GRAY,
    'hover_sc': color.GRAY,
    'hover_bd': 2,

    'press_bg': color.GRAY - offset_large,
    'press_sc': color.GRAY,
    'press_bd': 2,

    'ban_bg': color.LIGHTWHITE,
}

branch_list_button_style = {
    'origin_bg': color.LIGHTGREEN,
    'origin_sc': color.DEEPWHITE,
    'origin_bd': 2,

    'hover_bg': color.LIGHTGREEN + offset_small,

    'press_bg': color.LIGHTGREEN - offset_small,

    'ban_bg': color.LIGHTGREEN,
}

warn_button_style = {
    'origin_bg': color.LIGHTWHITE,
    'origin_sc': color.GRAY,
    'origin_bd': 2,

    'hover_bg': color.RED + offset_small,

    'press_bg': color.RED - offset_small,
    'ban_bg': color.RED,
}


del pygame, color
