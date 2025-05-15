import pygame
from pathlib import Path

import fantas
from fantas import uimanager as u

import Display.color as color
import Display.textstyle as textstyle
import Display.buttonstyle as buttonstyle

class NodeUi(fantas.IconText):
    numtext = chr(0xe6b5)

    def __init__(self, **kwargs):
        super().__init__(self.numtext, u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3, **kwargs)
