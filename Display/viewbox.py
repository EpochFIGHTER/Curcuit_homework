import pygame
from pathlib import Path

import fantas
from fantas import uimanager as u

import Display.color as color
import Display.textstyle as textstyle
import Display.buttonstyle as buttonstyle

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

    
class ProjectNameBox(fantas.InputLine):
    HEIGHT = 80
    PADDING = 20
    STYLE = { "text_pad": PADDING, "cursor_size": (4, 60), "cursor_bg": color.DARKBLUE }

    def __init__(self, **anchor):
        super().__init__((0, self.HEIGHT), u.fonts['deyi'], self.STYLE, textstyle.DARKBLUE_TITLE_2, maxinput=32, bd=2, sc=color.GRAY, bg=color.LIGHTWHITE, radius={"border_radius": 16}, mousewidget=ProjectNameMouseWidget, inputwidget=ProjectNameWidget, **anchor)
        self.set_text("新建电路图")
        self.anchor = 'right'

    def set_text(self, text):
        self.inputwidget.start_input()
        self.inputwidget.textinput(text)
        self.inputwidget.stop_input()
        self.update_size()

    def update_size(self):
        self.set_size((self.PADDING * 2 + self.text.rect.w + self.STYLE['cursor_size'][0], self.HEIGHT))
        self.endpos = self.origin_size[0] - self.startpos
        self.cursorpos = 0
        self.adapt()
        self.cursorpos = len(self.text.text)
        self.adapt()


project_name = ProjectNameBox(center=(viewbox.rect.w / 2, 120))
project_name.join(viewbox)

edit_name_button = fantas.SmoothColorButton((ProjectNameBox.HEIGHT, ProjectNameBox.HEIGHT), buttonstyle.edit_name_button_style, 2, radius={'border_radius': 16}, midleft=(project_name.rect.right + project_name.PADDING, project_name.rect.centery))
edit_name_button.bind(project_name.inputwidget.start_input)
edit_name_button.join(viewbox)
edit_icon = fantas.IconText(chr(0xe601), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_2, center=(edit_name_button.rect.w/2, edit_name_button.rect.h/2))
edit_icon.join(edit_name_button)

def import_diagram():
    pass

import_button = fantas.SmoothColorButton((ProjectNameBox.HEIGHT, ProjectNameBox.HEIGHT), buttonstyle.edit_name_button_style, 2, radius={'border_radius': 16}, midleft=(edit_name_button.rect.right + project_name.PADDING, project_name.rect.centery)) 
import_button.bind(import_diagram)
import_button.join(viewbox)
import_icon = fantas.IconText(chr(0xe65d), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_2, center=(import_button.rect.w/2, import_button.rect.h/2))
import_icon.join(import_button)

def export_diagram():
    pass

export_button = fantas.SmoothColorButton((ProjectNameBox.HEIGHT, ProjectNameBox.HEIGHT), buttonstyle.edit_name_button_style, 2, radius={'border_radius': 16}, midleft=(import_button.rect.right + project_name.PADDING, project_name.rect.centery))
export_button.bind(export_diagram)
export_button.join(viewbox)
export_icon = fantas.IconText(chr(0xe622), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_2, center=(export_button.rect.w/2, export_button.rect.h/2))
export_icon.join(export_button)

def build_new_diagram():
    pass

buildnew_button = fantas.SmoothColorButton((ProjectNameBox.HEIGHT, ProjectNameBox.HEIGHT), buttonstyle.edit_name_button_style, 2, radius={'border_radius': 16}, midleft=(export_button.rect.right + project_name.PADDING, project_name.rect.centery))
buildnew_button.bind(build_new_diagram)
buildnew_button.join(viewbox)
buildnew_icon = fantas.IconText(chr(0xe60f), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_2, center=(buildnew_button.rect.w/2, buildnew_button.rect.h/2))
buildnew_icon.join(buildnew_button)

class NumberInputLine(fantas.InputLine):
    pass

def layout():
    viewbox.join(u.root)
