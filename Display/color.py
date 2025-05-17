import pygame

BLACK      = pygame.Color("#000000")
FAKEWHITE  = pygame.Color("#e3e3e3")
DARKBLUE   = pygame.Color("#003658")
LIGHTWHITE = pygame.Color("#faf7ff")
DEEPWHITE  = pygame.Color("#c4c7cc")
THEMEBLUE  = pygame.Color("#8685ef")
GRAY       = pygame.Color("#aca9bb")
LIGHTGREEN  = pygame.Color("#c5ebde")

# 暗黑模式
def use_dark_mode():
    global BLACK, FAKEWHITE, DARKBLUE, LIGHTWHITE, DEEPWHITE, THEMEBLUE, GRAY, LIGHTGREEN
    BLACK      = pygame.Color("#ffffff") - BLACK
    FAKEWHITE  = pygame.Color("#ffffff") - FAKEWHITE
    DARKBLUE   = pygame.Color("#ffffff") - DARKBLUE
    LIGHTWHITE = pygame.Color("#ffffff") - LIGHTWHITE
    DEEPWHITE  = pygame.Color("#ffffff") - DEEPWHITE
    THEMEBLUE  = pygame.Color("#ffffff") - THEMEBLUE
    GRAY       = pygame.Color("#ffffff") - GRAY
    LIGHTGREEN  = pygame.Color("#ffffff") - LIGHTGREEN
    BLACK.a      = 255
    FAKEWHITE.a  = 255
    DARKBLUE.a   = 255
    LIGHTWHITE.a = 255
    DEEPWHITE.a  = 255
    THEMEBLUE.a  = 255
    GRAY.a       = 255
    LIGHTGREEN.a  = 255

del pygame
