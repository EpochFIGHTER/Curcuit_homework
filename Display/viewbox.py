import pygame
# from pathlib import Path

import fantas
from fantas import uimanager as u

import Display.color as color
import Display.textstyle as textstyle
import Display.buttonstyle as buttonstyle
import Display.inputstyle as inputstyle
from Display.widget import NumberInputWidget, UnitSwitchButton

from Core.Component import F_table

grid_size = 60
grid_line_width = 2

# class ViewBoxMouseWidget(fantas.MouseBase):
#     offset_curve_1 = fantas.FormulaCurve(f"math.sin(math.pi/{grid_size}*x)*{grid_size}/2")
#     offset_curve_2 = fantas.FormulaCurve(f"math.cos(math.pi*2/({grid_size}*5)*x-math.pi/5)*{grid_size}/4+{grid_size}/4")
#     offset_curve_3 = fantas.FormulaCurve(f"-math.cos(math.pi*2/({grid_size}*5)*(-x)-math.pi/5)*{grid_size}/4-{grid_size}/4")

#     def __init__(self, ui):
#         super().__init__(ui, 2)

#     def mousemove(self, pos):
#         if self.mouseon:
#             for v in range(len(v_lines)):
#                 offset = (v+1) * grid_size - pos[0]
#                 if grid_size / 2 <= offset <= grid_size * 3:
#                     offset = self.offset_curve_2.calc(offset)
#                 elif -grid_size / 2 <= offset < grid_size /2:
#                     offset = self.offset_curve_1.calc(offset)
#                 elif -grid_size * 3 <= offset < -grid_size / 2:
#                     offset = self.offset_curve_3.calc(offset)
#                 else:
#                     offset = 0
#                 v_lines[v].rect.centerx = (v+1) * grid_size + offset
#             for h in range(len(h_lines)):
#                 offset = (h+1) * grid_size - pos[1]
#                 if grid_size / 2 <= offset <= grid_size * 3:
#                     offset = self.offset_curve_2.calc(offset)
#                 elif -grid_size / 2 <= offset < grid_size /2:
#                     offset = self.offset_curve_1.calc(offset)
#                 elif -grid_size * 3 <= offset < -grid_size / 2:
#                     offset = self.offset_curve_3.calc(offset)
#                 else:
#                     offset = 0
#                 h_lines[h].rect.centery = (h+1) * grid_size + offset
#             self.ui.mark_update()

viewbox = fantas.Label((u.WIDTH * 3 / 4, u.HEIGHT), bg=color.FAKEWHITE, topleft=(0, 0))
# ViewBoxMouseWidget(viewbox).apply_event()

v_lines = []
for i in range(1, int(viewbox.rect.w / grid_size)):
    l = fantas.Label((grid_line_width, viewbox.rect.h), bg=color.GRAY, midtop=(i * grid_size, 0))
    l.join(viewbox)
    v_lines.append(l)

h_lines = []
for i in range(1, int(viewbox.rect.h / grid_size)):
    l = fantas.Label((viewbox.rect.w, grid_line_width), bg=color.GRAY, midleft=(0, i * grid_size))
    l.join(viewbox)
    h_lines.append(l)


class ProjectNameMouseWidget(fantas.InputLineMouseWidget):
    def mousepress(self, pos, button):
        if button == 1:
            if self.ui.inputwidget.inputing:
                if not self.mouseon:
                    self.ui.inputwidget.stop_input()

class ProjectNameWidget(fantas.InputLineWidget):
    def textedit(self, text, start):
        super().textedit(text, start)
        self.ui.update_size()
        self.ui.mark_update()

    def textinput(self, text):
        super().textinput(text)
        self.ui.update_size()
        self.ui.mark_update()

    def stop_input(self):
        super().stop_input()
        self.ui.update_size()
        self.ui.mark_update()


class ProjectNameBox(fantas.InputLine):
    HEIGHT = 80
    PADDING = 20

    def __init__(self, **anchor):
        super().__init__((0, self.HEIGHT), u.fonts['deyi'], inputstyle.normal_style, textstyle.DARKBLUE_TITLE_2, maxinput=32, bd=2, sc=color.GRAY, bg=color.LIGHTWHITE, radius={"border_radius": 16}, mousewidget=ProjectNameMouseWidget, inputwidget=ProjectNameWidget, **anchor)
        self.set_text("新建电路图")
        self.anchor = 'right'

    def set_text(self, text):
        self.inputwidget.start_input()
        self.inputwidget.textinput(text)
        self.inputwidget.stop_input()
        self.update_size()

    def update_size(self):
        self.set_size((self.PADDING * 2 + self.text.rect.w + self.style['cursor_size'][0], self.HEIGHT))
        self.endpos = self.origin_size[0] - self.startpos
        self.cursorpos = 0
        self.adapt()
        self.cursorpos = len(self.text.text)
        self.adapt()


project_name = ProjectNameBox(center=(viewbox.rect.w / 2, 120))
project_name.join(viewbox)

edit_name_button = fantas.SmoothColorButton((ProjectNameBox.HEIGHT, ProjectNameBox.HEIGHT), buttonstyle.common_button_style, 2, radius={'border_radius': 16}, midleft=(project_name.rect.right + project_name.PADDING, project_name.rect.centery))
edit_name_button.bind(project_name.inputwidget.start_input)
edit_name_button.join(viewbox)
edit_icon = fantas.IconText(chr(0xe601), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_2, center=(edit_name_button.rect.w/2, edit_name_button.rect.h/2))
edit_icon.join(edit_name_button)

def import_diagram():
    pass

import_button = fantas.SmoothColorButton((ProjectNameBox.HEIGHT, ProjectNameBox.HEIGHT), buttonstyle.common_button_style, 2, radius={'border_radius': 16}, midleft=(edit_name_button.rect.right + project_name.PADDING, project_name.rect.centery)) 
import_button.bind(import_diagram)
import_button.join(viewbox)
import_icon = fantas.IconText(chr(0xe65d), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_2, center=(import_button.rect.w/2, import_button.rect.h/2))
import_icon.join(import_button)

def export_diagram():
    pass

export_button = fantas.SmoothColorButton((ProjectNameBox.HEIGHT, ProjectNameBox.HEIGHT), buttonstyle.common_button_style, 2, radius={'border_radius': 16}, midleft=(import_button.rect.right + project_name.PADDING, project_name.rect.centery))
export_button.bind(export_diagram)
export_button.join(viewbox)
export_icon = fantas.IconText(chr(0xe622), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_2, center=(export_button.rect.w/2, export_button.rect.h/2))
export_icon.join(export_button)

def build_new_diagram():
    pass

buildnew_button = fantas.SmoothColorButton((ProjectNameBox.HEIGHT, ProjectNameBox.HEIGHT), buttonstyle.common_button_style, 2, radius={'border_radius': 16}, midleft=(export_button.rect.right + project_name.PADDING, project_name.rect.centery))
buildnew_button.bind(build_new_diagram)
buildnew_button.join(viewbox)
buildnew_icon = fantas.IconText(chr(0xe60f), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_2, center=(buildnew_button.rect.w/2, buildnew_button.rect.h/2))
buildnew_icon.join(buildnew_button)

def adapt():
    diagram_box.mousewidget.r = 1
    # diagram_box.size = (diagram_box.origin_size[0] * diagram_box.mousewidget.r, diagram_box.origin_size[1] * diagram_box.mousewidget.r)
    diagram_box.size_kf.value = (diagram_box.origin_size[0] * diagram_box.mousewidget.r, diagram_box.origin_size[1] * diagram_box.mousewidget.r)
    diagram_box.size_kf.launch("continue")
    diagram_box.mark_update()
    # diagram_box.rect.topleft = (0, 0)
    diagram_box.pos_kf.value = (0, 0)
    diagram_box.pos_kf.launch("continue")

adapt_button = fantas.SmoothColorButton((ProjectNameBox.HEIGHT, ProjectNameBox.HEIGHT), buttonstyle.common_button_style, 2, radius={'border_radius': 16}, midleft=(buildnew_button.rect.right + project_name.PADDING, project_name.rect.centery))
adapt_button.bind(adapt)
adapt_button.join(viewbox)
adapt_icon = fantas.IconText(chr(0xe64d), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_2, center=(adapt_button.rect.w/2, adapt_button.rect.h/2))
adapt_icon.join(adapt_button)

class FreqInputLineWidget(NumberInputWidget):
    def stop_input(self):
        super().stop_input()
        self.ui.update_size()
        self.ui.mark_update()

    def textedit(self, text, start):
        super().textedit(text, start)
        self.ui.update_size()
        self.ui.mark_update()

    def textinput(self, text):
        super().textinput(text)
        self.ui.update_size()
        self.ui.mark_update()

class FreqInputLine(fantas.InputLine):
    HEIGHT = 40

    def __init__(self, **anchor):
        super().__init__((0, self.HEIGHT), u.fonts['deyi'], inputstyle.small_style, textstyle.DARKBLUE_TITLE_4, "输入频率", 32, FreqInputLineWidget, bd=2, sc=color.GRAY, bg=color.LIGHTWHITE, radius={ 'border_radius': 12 }, **anchor)
        self.anchor = 'right'
        self.update_size()

    def update_size(self):
        if self.text.text == "" and self.tiptext is not None:
            self.set_size((self.style['text_pad'] * 2 + self.tiptext.rect.w + self.style['cursor_size'][0], self.rect.h))
        else:
            self.set_size((self.style['text_pad'] * 2 + self.text.rect.w + self.style['cursor_size'][0], self.rect.h))
        self.endpos = self.origin_size[0] - self.startpos
        self.cursorpos = 0
        self.adapt()
        self.cursorpos = len(self.text.text)
        self.adapt()

freq_inputline = FreqInputLine(bottomright=(viewbox.rect.w - ProjectNameBox.HEIGHT, viewbox.rect.h - ProjectNameBox.HEIGHT / 2))
freq_inputline.join(viewbox)
freq_unit_switch_button = UnitSwitchButton(F_table, midleft=(freq_inputline.rect.right + freq_inputline.HEIGHT / 4, freq_inputline.rect.centery))
freq_unit_switch_button.join(viewbox)

class DiagramBoxMouuseWidget(fantas.MouseBase):
    SCALESPEED = 0.05
    
    def __init__(self, ui):
        super().__init__(ui, 3)
        self.pressed_pos = None
        self.start_pos = None
        self.r = 1

    def mousepress(self, pos, button):
        if button == pygame.BUTTON_LEFT and 0 < pos[0] < viewbox.rect.w - 80 and 150 < pos[1] < viewbox.rect.h - 80:
            self.pressed_pos = pos
            self.start_pos = self.ui.rect.topleft

    def mouserelease(self, pos, button):
        if self.pressed_pos is not None:
            self.pressed_pos = None

    def mousemove(self, pos):
        if self.pressed_pos is not None:
            self.ui.pos_kf.value = (self.start_pos[0] + pos[0] - self.pressed_pos[0], self.start_pos[1] + pos[1] - self.pressed_pos[1])
            self.ui.pos_kf.launch("continue")
            # self.ui.rect.topleft = (self.start_pos[0] + pos[0] - self.pressed_pos[0], self.start_pos[1] + pos[1] - self.pressed_pos[1])
            self.ui.father.mark_update()

    def mousescroll(self, x, y):
        pos = pygame.mouse.get_pos()
        if 0 < pos[0] < viewbox.rect.w - 80 and 150 < pos[1] < viewbox.rect.h - 80:
            self.r += y * self.SCALESPEED
            if self.r < 0.25:
                self.r = 0.25
            elif self.r > 2:
                self.r = 2
            # self.ui.size = (self.ui.origin_size[0] * self.r, self.ui.origin_size[1] * self.r)
            self.ui.size_kf.value = (self.ui.origin_size[0] * self.r, self.ui.origin_size[1] * self.r)
            self.ui.size_kf.launch("continue")
            self.ui.mark_update()

class DiagramBox(fantas.Ui):
    def __init__(self):
        super().__init__(pygame.Surface((0, 0), pygame.SRCALPHA))
        self.mousewidget = DiagramBoxMouuseWidget(self)
        self.mousewidget.apply_event()
        self.size_kf = fantas.UiKeyFrame(self, 'size', self.size, 10, fantas.slower_curve)
        self.pos_kf = fantas.RectKeyFrame(self, 'topleft', self.rect.topleft, 10, fantas.slower_curve)

    def update(self, anchor=None):
        w = max((ui.rect.right for ui in self.kidgroup), default=0)
        h = max((ui.rect.bottom for ui in self.kidgroup), default=0)
        self.img = pygame.Surface((w, h), pygame.SRCALPHA)
        self.size = (w, h)
        self.apply_size()

diagram_box = DiagramBox()
diagram_box.join_to(viewbox, project_name.get_index())

class NodeUi(fantas.IconText):
    numtext = chr(0xe6b5)

    def __init__(self, node_num):
        self.node_num = node_num
        super().__init__(self.numtext, u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3, center=(viewbox.rect.w * (node_num * 2 + 1) / 8, viewbox.rect.h / 2))
        self.name = fantas.Text(f"n{node_num}", u.fonts['shuhei'], textstyle.DARKBLUE_TITLE_3, topright=self.rect.bottomleft)

    def join(self, node):
        super().join(node)
        self.name.join(node)

node_0_icon = NodeUi(0)
node_1_icon = NodeUi(1)
node_2_icon = NodeUi(2)
node_3_icon = NodeUi(3)
node_0_icon.join(diagram_box)
node_1_icon.join(diagram_box)
node_2_icon.join(diagram_box)
node_3_icon.join(diagram_box)

diagram_box.anchor = 'topleft'
diagram_box.update()

switch_color_button = fantas.SmoothColorButton((ProjectNameBox.HEIGHT, ProjectNameBox.HEIGHT), buttonstyle.common_button_style, 2, radius={'border_radius': 16}, bottomleft=(ProjectNameBox.HEIGHT / 2, viewbox.rect.h - ProjectNameBox.HEIGHT / 2))
switch_color_button.join(viewbox)
switch_color_icon = fantas.IconText(chr(0xe959 if color.IS_DARKMODE else 0xe76b), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_2, center=(switch_color_button.rect.w/2, switch_color_button.rect.h/2))
switch_color_icon.join(switch_color_button)

def switch_color():
    color.switch_dark_mode()
    if color.IS_DARKMODE:
        switch_color_icon.text = chr(0xe959)
    else:
        switch_color_icon.text = chr(0xe76b)
    switch_color_icon.update_img()
switch_color_button.bind(switch_color)



def layout():
    viewbox.join(u.root)
