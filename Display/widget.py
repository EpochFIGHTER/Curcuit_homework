import pygame
from pathlib import Path

import fantas
from fantas import uimanager as u

import Display.color as color
import Display.textstyle as textstyle
import Display.buttonstyle as buttonstyle


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class NumberInputWidget(fantas.InputLineWidget):
    def stop_input(self):
        super().stop_input()
        if not is_number(self.ui.text.text):
            self.ui.clear()


class UnitSwitchButton(fantas.SmoothColorButton):
    WIDTH = 40
    HEIGHT = 40

    def __init__(self, unit_table, **anchor):
        super().__init__((self.WIDTH, self.HEIGHT), buttonstyle.common_button_style, 2, radius={'border_radius': 12}, **anchor)
        self.unit_table = unit_table
        self.unit = 0
        self.text = fantas.Text(self.unit_table[self.unit], u.fonts['deyi'], textstyle.DARKBLUE_TITLE_4, center=(self.rect.w / 2, self.rect.h / 2))
        self.text.join(self)
        self.bind(self.switch)

    def switch(self):
        self.unit = (self.unit + 1) % len(self.unit_table)
        self.text.text = self.unit_table[self.unit]
        self.text.update_img()
        self.mark_update()
