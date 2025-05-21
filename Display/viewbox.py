import pygame
# from pathlib import Path

import fantas
from fantas import uimanager as u

import Display.color as color
import Display.textstyle as textstyle
import Display.buttonstyle as buttonstyle
import Display.inputstyle as inputstyle
from Display.widget import NumberInputWidget, UnitSwitchButton
import Display.sidebar as sidebar

from Core.Component import F_table, nodes
import Core

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
        self.clear()
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
    project_name.set_text("新建电路图")
    for b in list(sidebar.branch_list.kidgroup):
        if isinstance(b, sidebar.BranchUi):
            b.delete()
    sidebar.branch_list.top_kf.value = 0
    sidebar.branch_list.top_kf.launch("continue")
    adapt()

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
freq_inputline.inputwidget.start_input()
freq_inputline.inputwidget.textinput("1")
freq_inputline.inputwidget.stop_input()
freq_unit_switch_button.switch()

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
            if self.r < 0.2:
                self.r = 0.2
            elif self.r > 2:
                self.r = 2
            # self.ui.size = (self.ui.origin_size[0] * self.r, self.ui.origin_size[1] * self.r)
            self.ui.size_kf.value = (self.ui.origin_size[0] * self.r, self.ui.origin_size[1] * self.r)
            self.ui.size_kf.launch("continue")
            self.ui.mark_update()

COMPONENT_SIZE = (180, 80)
BRANCH_WIDTH = 4
LEFT_FLAG_POS = (40, 20)
RIGHT_FLAG_POS = (140, 20)

class DataCheckMouseWidget(fantas.MouseBase):
    RECT = pygame.Rect((0, 150, viewbox.rect.w - 80, viewbox.rect.h - 230))
    
    def __init__(self, ui, component):
        super().__init__(ui, 2)
        self.component = component

    def mousepress(self, pos, button):
        if not sidebar.caculated_flag:
            return
        if button == pygame.BUTTON_LEFT:
            rect = pygame.Rect(self.ui.rect)
            rect.w *= diagram_box.mousewidget.r
            rect.h *= diagram_box.mousewidget.r
            rect.left *= diagram_box.mousewidget.r
            rect.top *= diagram_box.mousewidget.r
            if self.RECT.collidepoint(pygame.mouse.get_pos()) and rect.collidepoint(pos):
                sidebar.show_data(self.component)

class DiagramBox(fantas.Ui):
    def __init__(self):
        super().__init__(pygame.Surface((0, 0), pygame.SRCALPHA))
        self.mousewidget = DiagramBoxMouuseWidget(self)
        self.mousewidget.apply_event()
        self.size_kf = fantas.UiKeyFrame(self, 'size', self.size, 10, fantas.slower_curve)
        self.pos_kf = fantas.RectKeyFrame(self, 'topleft', self.rect.topleft, 10, fantas.slower_curve)
        self.diagram_widgets = []

    def update(self):
        self.clear_widgets()
        self.draw_widgets()
        t = min((ui.rect.top for ui in self.kidgroup), default=0)
        w = max((ui.rect.right for ui in self.kidgroup), default=0)
        h = max((ui.rect.bottom for ui in self.kidgroup), default=0)
        self.img = pygame.Surface((w, h), pygame.SRCALPHA)
        # self.img.fill((255, 255, 255, 255))
        if t < 0:
            h -= t
            # self.rect.top += t
            for k in self.kidgroup:
                k.rect.top -= t
        self.size = (w, h)
        self.apply_size()
        self.size = self.size_kf.value = (w * self.mousewidget.r, h * self.mousewidget.r)

    def draw_widgets(self):
        global nodes, nodeuis, diagram_box, NodeUi
        record = (
            [0, False, 0],
            [0, False, 0],
            [0, False, 0],
        )    # 记录绘制空间占用情况

        distance = [viewbox.rect.w / 4, viewbox.rect.w / 4, viewbox.rect.w / 4]    # 节点之间的距离
        l = max((len(b) for b in nodes[0].branches.get(nodes[1], [])), default=0) + 1
        if l > 1:
            distance[0] = l * COMPONENT_SIZE[0]
        l = max((len(b) for b in nodes[1].branches.get(nodes[2], [])), default=0) + 1
        if l > 1:
            distance[1] = l * COMPONENT_SIZE[0]
        l = max((len(b) for b in nodes[0].branches.get(nodes[2], [])), default=0) + 1
        distance[1] = max(COMPONENT_SIZE[0] * l - distance[0], distance[1])
        l = max((len(b) for b in nodes[2].branches.get(nodes[3], [])), default=0) + 1
        if l > 1:
            distance[2] = l * COMPONENT_SIZE[0]
        l = max((len(b) for b in nodes[1].branches.get(nodes[3], [])), default=0) + 1
        distance[2] = max(COMPONENT_SIZE[0] * l - distance[1], distance[2])
        l = max((len(b) for b in nodes[0].branches.get(nodes[3], [])), default=0) + 1
        distance[2] = max(COMPONENT_SIZE[0] * l - distance[0] - distance[1], distance[2])

        for i in range(3):
            nodeuis[i + 1].rect.centerx = nodeuis[i].rect.centerx + distance[i]
            nodeuis[i + 1].name.rect.topright = nodeuis[i + 1].rect.bottomleft
        # 绘制相邻支路
        for i in range(3):
            node1 = nodes[i]
            node2 = nodes[i + 1]
            for b in node1.branches.get(node2, []):
                if record[i][1]:    #中间有连接
                    uh = record[i][0]    # 上方高度
                    dh = record[i][2]    # 下方高度
                    if uh <= dh:    # 在上方绘制
                        uh += 1
                        record[i][0]  = uh
                        l1 = fantas.Label((BRANCH_WIDTH, COMPONENT_SIZE[1] * 2 * uh - NodeUi.SIZE / 2), bg=color.DARKBLUE, radius={"border_top_left_radius": BRANCH_WIDTH // 2, "border_top_right_radius": BRANCH_WIDTH // 2}, midbottom=(nodeuis[i].rect.centerx, nodeuis[i].rect.centery - NodeUi.SIZE / 2))
                        l2 = fantas.Label((BRANCH_WIDTH, COMPONENT_SIZE[1] * 2 * uh - NodeUi.SIZE / 2), bg=color.DARKBLUE, radius={"border_top_left_radius": BRANCH_WIDTH // 2, "border_top_right_radius": BRANCH_WIDTH // 2}, midbottom=(nodeuis[i + 1].rect.centerx, nodeuis[i + 1].rect.centery - NodeUi.SIZE / 2))
                        l3 = fantas.Label((distance[i] + BRANCH_WIDTH, BRANCH_WIDTH), bg=color.DARKBLUE, radius={"border_radius": BRANCH_WIDTH // 2}, topleft=(nodeuis[i].rect.centerx - BRANCH_WIDTH // 2, nodeuis[i].rect.centery - COMPONENT_SIZE[1] * 2 * uh))
                    else:           # 在下方绘制
                        dh += 1
                        record[i][2]  = dh
                        l1 = fantas.Label((BRANCH_WIDTH, COMPONENT_SIZE[1] * 2 * dh - NodeUi.SIZE / 2), bg=color.DARKBLUE, radius={"border_bottom_left_radius": BRANCH_WIDTH // 2, "border_bottom_right_radius": BRANCH_WIDTH // 2}, midtop=(nodeuis[i].rect.centerx, nodeuis[i].rect.centery + NodeUi.SIZE / 2))
                        l2 = fantas.Label((BRANCH_WIDTH, COMPONENT_SIZE[1] * 2 * dh - NodeUi.SIZE / 2), bg=color.DARKBLUE, radius={"border_bottom_left_radius": BRANCH_WIDTH // 2, "border_bottom_right_radius": BRANCH_WIDTH // 2}, midtop=(nodeuis[i + 1].rect.centerx, nodeuis[i + 1].rect.centery + NodeUi.SIZE / 2))
                        l3 = fantas.Label((distance[i] + BRANCH_WIDTH, BRANCH_WIDTH), bg=color.DARKBLUE, radius={"border_radius": BRANCH_WIDTH // 2}, bottomleft=(nodeuis[i].rect.centerx - BRANCH_WIDTH // 2, nodeuis[i].rect.centery + COMPONENT_SIZE[1] * 2 * dh))
                    l1.join(diagram_box)
                    l2.join(diagram_box)
                    l3.join(diagram_box)
                    self.diagram_widgets.append(l1)
                    self.diagram_widgets.append(l2)
                    self.diagram_widgets.append(l3)
                    self.draw_component(b, l3)
                else:               # 中间没有连接，直接画在中间
                    record[i][1] = True
                    l = fantas.Label((distance[i] - NodeUi.SIZE, BRANCH_WIDTH), bg=color.DARKBLUE, midleft=(nodeuis[i].rect.centerx + NodeUi.SIZE / 2, nodeuis[i].rect.centery))
                    l.join(diagram_box)
                    self.diagram_widgets.append(l)
                    self.draw_component(b, l)
        # 绘制隔一个节点的支路
        for i in range(2):
            node1 = nodes[i]
            node2 = nodes[i + 2]
            for b in node1.branches.get(node2, []):
                uh = max(record[i][0], record[i + 1][0])    # 上方高度
                dh = max(record[i][2], record[i + 1][2])    # 下方高度
                d = distance[i] + distance[i + 1]           # 节点之间的距离
                if i == 0:    # 在上方绘制
                    uh += 1
                    record[i][0] = uh
                    record[i + 1][0] = uh
                    l1 = fantas.Label((BRANCH_WIDTH, COMPONENT_SIZE[1] * 2 * uh - NodeUi.SIZE / 2), bg=color.DARKBLUE, radius={"border_top_left_radius": BRANCH_WIDTH // 2, "border_top_right_radius": BRANCH_WIDTH // 2}, midbottom=(nodeuis[i].rect.centerx, nodeuis[i].rect.centery - NodeUi.SIZE / 2))
                    l2 = fantas.Label((BRANCH_WIDTH, COMPONENT_SIZE[1] * 2 * uh - NodeUi.SIZE / 2), bg=color.DARKBLUE, radius={"border_top_left_radius": BRANCH_WIDTH // 2, "border_top_right_radius": BRANCH_WIDTH // 2}, midbottom=(nodeuis[i + 2].rect.centerx, nodeuis[i + 2].rect.centery - NodeUi.SIZE / 2))
                    l3 = fantas.Label((d + BRANCH_WIDTH, BRANCH_WIDTH), bg=color.DARKBLUE, radius={"border_radius": BRANCH_WIDTH // 2}, topleft=(nodeuis[i].rect.centerx - BRANCH_WIDTH // 2, nodeuis[i].rect.centery - COMPONENT_SIZE[1] * 2 * uh))
                else:           # 在下方绘制
                    dh += 1
                    record[i][2] = dh
                    record[i + 1][2] = dh
                    l1 = fantas.Label((BRANCH_WIDTH, COMPONENT_SIZE[1] * 2 * dh - NodeUi.SIZE / 2), bg=color.DARKBLUE, radius={"border_bottom_left_radius": BRANCH_WIDTH // 2, "border_bottom_right_radius": BRANCH_WIDTH // 2}, midtop=(nodeuis[i].rect.centerx, nodeuis[i].rect.centery + NodeUi.SIZE / 2))
                    l2 = fantas.Label((BRANCH_WIDTH, COMPONENT_SIZE[1] * 2 * dh - NodeUi.SIZE / 2), bg=color.DARKBLUE, radius={"border_bottom_left_radius": BRANCH_WIDTH // 2, "border_bottom_right_radius": BRANCH_WIDTH // 2}, midtop=(nodeuis[i + 2].rect.centerx, nodeuis[i + 2].rect.centery + NodeUi.SIZE / 2))
                    l3 = fantas.Label((d + BRANCH_WIDTH, BRANCH_WIDTH), bg=color.DARKBLUE, radius={"border_radius": BRANCH_WIDTH // 2}, bottomleft=(nodeuis[i].rect.centerx - BRANCH_WIDTH // 2, nodeuis[i].rect.centery + COMPONENT_SIZE[1] * 2 * dh))
                l1.join(diagram_box)
                l2.join(diagram_box)
                l3.join(diagram_box)
                self.diagram_widgets.append(l1)
                self.diagram_widgets.append(l2)
                self.diagram_widgets.append(l3)
                self.draw_component(b, l3)
        # 绘制隔两个节点的支路
        node1 = nodes[0]
        node2 = nodes[3]
        for b in node1.branches.get(node2, []):
            uh = max(record[0][0], record[1][0], record[2][0])
            dh = max(record[0][2], record[1][2], record[2][2])
            d = distance[0] + distance[1] + distance[2]
            if uh <= dh:    # 在上方绘制
                uh += 1
                record[0][0] = uh
                record[1][0] = uh
                record[2][0] = uh
                l1 = fantas.Label((BRANCH_WIDTH, COMPONENT_SIZE[1] * 2 * uh - NodeUi.SIZE / 2), bg=color.DARKBLUE, radius={"border_top_left_radius": BRANCH_WIDTH // 2, "border_top_right_radius": BRANCH_WIDTH // 2}, midbottom=(nodeuis[0].rect.centerx, nodeuis[0].rect.centery - NodeUi.SIZE / 2))
                l2 = fantas.Label((BRANCH_WIDTH, COMPONENT_SIZE[1] * 2 * uh - NodeUi.SIZE / 2), bg=color.DARKBLUE, radius={"border_top_left_radius": BRANCH_WIDTH // 2, "border_top_right_radius": BRANCH_WIDTH // 2}, midbottom=(nodeuis[3].rect.centerx, nodeuis[3].rect.centery - NodeUi.SIZE / 2))
                l3 = fantas.Label((d + BRANCH_WIDTH, BRANCH_WIDTH), bg=color.DARKBLUE, radius={"border_radius": BRANCH_WIDTH // 2}, topleft=(nodeuis[0].rect.centerx - BRANCH_WIDTH // 2, nodeuis[0].rect.centery - COMPONENT_SIZE[1] * 2 * uh))
            else:           # 在下方绘制
                dh += 1
                record[0][2] = dh
                record[1][2] = dh
                record[2][2] = dh
                l1 = fantas.Label((BRANCH_WIDTH, COMPONENT_SIZE[1] * 2 * dh - NodeUi.SIZE / 2), bg=color.DARKBLUE, radius={"border_bottom_left_radius": BRANCH_WIDTH // 2, "border_bottom_right_radius": BRANCH_WIDTH // 2}, midtop=(nodeuis[0].rect.centerx, nodeuis[0].rect.centery + NodeUi.SIZE / 2))
                l2 = fantas.Label((BRANCH_WIDTH, COMPONENT_SIZE[1] * 2 * dh - NodeUi.SIZE / 2), bg=color.DARKBLUE, radius={"border_bottom_left_radius": BRANCH_WIDTH // 2, "border_bottom_right_radius": BRANCH_WIDTH // 2}, midtop=(nodeuis[3].rect.centerx, nodeuis[3].rect.centery + NodeUi.SIZE / 2))
                l3 = fantas.Label((d + BRANCH_WIDTH, BRANCH_WIDTH), bg=color.DARKBLUE, radius={"border_radius": BRANCH_WIDTH // 2}, bottomleft=(nodeuis[0].rect.centerx - BRANCH_WIDTH // 2, nodeuis[0].rect.centery + COMPONENT_SIZE[1] * 2 * dh))
            l1.join(diagram_box)
            l2.join(diagram_box)
            l3.join(diagram_box)
            self.diagram_widgets.append(l1)
            self.diagram_widgets.append(l2)
            self.diagram_widgets.append(l3)
            self.draw_component(b, l3)

    def clear_widgets(self):
        for ui in self.diagram_widgets:
            ui.leave()
        self.diagram_widgets.clear()

    def draw_component(self, branch, branch_line):
        l = len(branch)
        if l == 0:
            return
        pad = branch_line.rect.w / (l + 1)
        index = 1
        for c in branch:
            img_name = c.IMG_NAME
            if color.IS_DARKMODE:
                img_name = "DARK_" + img_name
            i = fantas.Ui(u.images[img_name], center=(branch_line.rect.left + index * pad, branch_line.rect.centery))
            DataCheckMouseWidget(i, c).apply_event()
            index += 1
            l = fantas.Label((130, BRANCH_WIDTH), bg=color.FAKEWHITE, center=i.rect.center)
            n = fantas.Text(f"{c.prefix}{c.num}", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midtop=i.rect.midbottom)
            l.join(diagram_box)
            i.join(diagram_box)
            n.join(diagram_box)
            self.diagram_widgets.append(i)
            self.diagram_widgets.append(l)
            self.diagram_widgets.append(n)
            if isinstance(c, Core.Resistor):
                if c.R is not None:
                    r, unit = Core.intelligent_output(c.R, Core.R_table, Core.R_k)
                    d = fantas.Text(f"{r:.2f}{unit}", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midbottom=i.rect.midtop)
                    d.join(diagram_box)
                    self.diagram_widgets.append(d)
            elif isinstance(c, Core.Capacitor):
                if c.C is not None:
                    r, unit = Core.intelligent_output(c.C, Core.C_table, Core.C_k)
                    d = fantas.Text(f"{r:.2f}{unit}", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midbottom=i.rect.midtop)
                    d.join(diagram_box)
                    self.diagram_widgets.append(d)
            elif isinstance(c, Core.Inductor):
                if c.L is not None:
                    r, unit = Core.intelligent_output(c.L, Core.L_table, Core.L_k)
                    d = fantas.Text(f"{r:.2f}{unit}", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midbottom=i.rect.midtop)
                    d.join(diagram_box)
                    self.diagram_widgets.append(d)
            elif isinstance(c, Core.Impedance):
                if c.Z is not None:
                    v, p = Core.get_vp(c.Z)
                    r, unit = Core.intelligent_output(v, Core.R_table, Core.R_k)
                    d = fantas.Text(f"{r:.2f}", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, bottomright=i.rect.midtop)
                    d.join(diagram_box)
                    self.diagram_widgets.append(d)
                    d = fantas.IconText(chr(0xe619), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3, midleft=d.rect.midright)
                    d.join(diagram_box)
                    self.diagram_widgets.append(d)
                    d = fantas.Text(f"{p:.2f}°{unit}", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midleft=d.rect.midright)
                    d.join(diagram_box)
                    self.diagram_widgets.append(d)
            elif isinstance(c, Core.IndependentVoltageSource):
                p = fantas.Text("+", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3)
                n = fantas.Text("-", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3)
                p.join(diagram_box)
                n.join(diagram_box)
                self.diagram_widgets.append(p)
                self.diagram_widgets.append(n)
                if c.Vref:
                    p.rect.centerx = LEFT_FLAG_POS[0] + i.rect.left
                    p.rect.centery = LEFT_FLAG_POS[1] + i.rect.top
                    n.rect.centerx = RIGHT_FLAG_POS[0] + i.rect.left
                    n.rect.centery = RIGHT_FLAG_POS[1] + i.rect.top
                else:
                    p.rect.centerx = RIGHT_FLAG_POS[0] + i.rect.left
                    p.rect.centery = RIGHT_FLAG_POS[1] + i.rect.top
                    n.rect.centerx = LEFT_FLAG_POS[0] + i.rect.left
                    n.rect.centery = LEFT_FLAG_POS[1] + i.rect.top
                if c.U is not None:
                    v, p = Core.get_vp(c.U)
                    U, unit = Core.intelligent_output(v, Core.V_table, Core.V_k)
                    d = fantas.Text(f"{U:.2f}", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, bottomright=i.rect.midtop)
                    d.join(diagram_box)
                    self.diagram_widgets.append(d)
                    d = fantas.IconText(chr(0xe619), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3, midleft=d.rect.midright)
                    d.join(diagram_box)
                    self.diagram_widgets.append(d)
                    d = fantas.Text(f"{p:.2f}°{unit}", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midleft=d.rect.midright)
                    d.join(diagram_box)
                    self.diagram_widgets.append(d)
            elif isinstance(c, Core.IndependentCurrentSource):
                a = fantas.IconText(chr(0xe60e), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_1, centery=i.rect.centery)
                a.join(diagram_box)
                self.diagram_widgets.append(a)
                if c.Iref:
                    a.angle = 90
                    a.rect.centerx = RIGHT_FLAG_POS[0] + i.rect.left + 10
                else:
                    a.angle = -90
                    a.rect.centerx = LEFT_FLAG_POS[0] + i.rect.left - 10
                if c.I is not None:
                    v, p = Core.get_vp(c.I)
                    I, unit = Core.intelligent_output(v, Core.I_table, Core.I_k)
                    d = fantas.Text(f"{I:.2f}", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, bottomright=i.rect.midtop)
                    d.join(diagram_box)
                    self.diagram_widgets.append(d)
                    d = fantas.IconText(chr(0xe619), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3, midleft=d.rect.midright)
                    d.join(diagram_box)
                    self.diagram_widgets.append(d)
                    d = fantas.Text(f"{p:.2f}°{unit}", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midleft=d.rect.midright)
                    d.join(diagram_box)
                    self.diagram_widgets.append(d)
            elif isinstance(c, Core.DependentVoltageSource):
                p = fantas.Text("+", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3)
                n = fantas.Text("-", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3)
                p.join(diagram_box)
                n.join(diagram_box)
                self.diagram_widgets.append(p)
                self.diagram_widgets.append(n)
                if c.Vref:
                    p.rect.centerx = LEFT_FLAG_POS[0] + i.rect.left
                    p.rect.centery = LEFT_FLAG_POS[1] + i.rect.top
                    n.rect.centerx = RIGHT_FLAG_POS[0] + i.rect.left
                    n.rect.centery = RIGHT_FLAG_POS[1] + i.rect.top
                else:
                    p.rect.centerx = RIGHT_FLAG_POS[0] + i.rect.left
                    p.rect.centery = RIGHT_FLAG_POS[1] + i.rect.top
                    n.rect.centerx = LEFT_FLAG_POS[0] + i.rect.left
                    n.rect.centery = LEFT_FLAG_POS[1] + i.rect.top
                if c.k is not None and c.controler is not None:
                    d = fantas.Text(f"{c.k:.2f}{c.value} ({c.controler.prefix}{c.controler.num})", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midbottom=i.rect.midtop)
                    d.join(diagram_box)
                    self.diagram_widgets.append(d)
            elif isinstance(c, Core.DependentCurrentSource):
                a = fantas.IconText(chr(0xe60e), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_1, centery=i.rect.centery)
                a.join(diagram_box)
                self.diagram_widgets.append(a)
                if c.Iref:
                    a.angle = 90
                    a.rect.centerx = RIGHT_FLAG_POS[0] + i.rect.left + 10
                else:
                    a.angle = -90
                    a.rect.centerx = LEFT_FLAG_POS[0] + i.rect.left - 10
                if c.k is not None and c.controler is not None:
                    d = fantas.Text(f"{c.k:.2f}{c.value} ({c.controler.prefix}{c.controler.num})", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midbottom=i.rect.midtop)
                    d.join(diagram_box)
                    self.diagram_widgets.append(d)

diagram_box = DiagramBox()
diagram_box.join_to(viewbox, project_name.get_index())

class NodeUi(fantas.IconText):
    numtext = chr(0xe6b5)
    SIZE = 16

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

nodeuis = [node_0_icon, node_1_icon, node_2_icon, node_3_icon]

diagram_box.anchor = 'topleft'
diagram_box.update()

switch_color_button = fantas.SmoothColorButton((ProjectNameBox.HEIGHT, ProjectNameBox.HEIGHT), buttonstyle.common_button_style, 2, radius={'border_radius': 16}, bottomleft=(ProjectNameBox.HEIGHT / 2, viewbox.rect.h - ProjectNameBox.HEIGHT / 2))
switch_color_button.join(viewbox)
switch_color_icon = fantas.IconText(chr(0xe959 if color.IS_DARKMODE else 0xe76b), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_2, center=(switch_color_button.rect.w/2, switch_color_button.rect.h/2))
switch_color_icon.join(switch_color_button)

def switch_color():
    u.settings['DARK_MODE'] = not u.settings['DARK_MODE']
    if u.settings['DARK_MODE']:
        switch_color_icon.text = chr(0xe959)
    else:
        switch_color_icon.text = chr(0xe76b)
    switch_color_icon.update_img()
switch_color_button.bind(switch_color)



def layout():
    viewbox.join(u.root)
