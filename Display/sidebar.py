import sys
import math
import cmath
import pygame
# from pathlib import Path

import fantas
from fantas import uimanager as u

import Display.color as color
import Display.textstyle as textstyle
import Display.buttonstyle as buttonstyle
import Display.inputstyle as inputstyle
import Display.viewbox as viewbox

from Display.widget import NumberInputWidget, UnitSwitchButton

from Core.Component import nodes, ElectricalBranch, Resistor, Capacitor, Inductor, Impedance, IndependentVoltageSource, IndependentCurrentSource, DependentVoltageSource, DependentCurrentSource
from Core.simulate import solve_circuit, print_circuit_solution
import Core

SIDEBAR_LEFT = u.WIDTH / 4 * 3


class SidebarPageMouseWidget(fantas.MouseBase):
    def __init__(self, page):
        super().__init__(page, 2)
    
    def mousein(self):
        if not self.ui.poped and not self.ui.pre_poped:
            self.ui.pre_pop()

    def mouseout(self):
        if not self.ui.poped and self.ui.pre_poped:
            self.ui.back()
    
    def mouseclick(self):
        if self.mousedown == pygame.BUTTON_LEFT:
            if not self.ui.poped:
                self.ui.pop()


class SidebarPage(fantas.Label):
    WIDTH = 40
    PADDING = 10
    RADIUS = 10
    NEXT_TOP = 10
    objects = []

    def __init__(self, title):
        SidebarPage.objects.append(self)
        self.poped = False
        self.pre_poped = False
        start_pos = SidebarPage.PADDING
        self.title_text = []
        for s in title:
            t = fantas.Text(s, u.fonts['deyi'], textstyle.GRAY_TITLE_4, midtop=(SidebarPage.WIDTH / 2, start_pos))
            self.title_text.append(t)
            start_pos += t.rect.h
        self.HEIGHT = start_pos + SidebarPage.PADDING
        super().__init__((SidebarPage.WIDTH, self.HEIGHT), bd=2, bg=color.DEEPWHITE, sc=color.GRAY, radius={"border_top_left_radius": self.RADIUS, "border_bottom_left_radius": self.RADIUS}, topright=(SIDEBAR_LEFT, SidebarPage.NEXT_TOP))
        self.anchor = "right"
        SidebarPage.NEXT_TOP += self.rect.h - SidebarPage.PADDING
        self.page = fantas.Label((u.WIDTH / 4, u.HEIGHT), bg=color.FAKEWHITE, topright=(u.WIDTH, 0))
        for t in self.title_text:
            t.join(self)

        self.mousewidget = SidebarPageMouseWidget(self)
        self.mousewidget.apply_event()

        self.size_kf = fantas.LabelKeyFrame(self, 'size', (self.WIDTH, self.HEIGHT), 10, fantas.harmonic_curve)
        self.sc_kf = fantas.LabelKeyFrame(self, 'sc', color.DARKBLUE, 10, fantas.curve)
        self.bg_kf = fantas.LabelKeyFrame(self, 'bg', color.FAKEWHITE, 10, fantas.curve)
        self.title_text_fg_kf = []
        for t in self.title_text:
            self.title_text_fg_kf.append(fantas.TextKeyFrame(t, 'fgcolor', color.DARKBLUE, 10, fantas.curve))

    def pre_pop(self):
        self.pre_poped = True
        self.size_kf.value = (self.WIDTH + self.PADDING, self.HEIGHT)
        self.size_kf.launch('continue')

    def pop(self):
        self.poped = True
        self.size_kf.value = (self.WIDTH + self.PADDING, self.HEIGHT)
        self.size_kf.launch('continue')
        self.sc_kf.value = color.DARKBLUE
        self.sc_kf.launch('continue')
        self.bg_kf.value = color.FAKEWHITE
        self.bg_kf.launch('continue')
        for t in self.title_text_fg_kf:
            t.value = color.DARKBLUE
            t.launch('continue')

        for i in range(len(SidebarPage.objects), 0, -1):
            SidebarPage.objects[i - 1].leave()
            SidebarPage.objects[i - 1].join(u.root)
            if SidebarPage.objects[i - 1] != self and SidebarPage.objects[i - 1].poped:
                SidebarPage.objects[i - 1].back()

        self.page.join(u.root)

    def back(self):
        self.poped = False
        self.pre_poped = False
        self.size_kf.value = (self.WIDTH, self.HEIGHT)
        self.size_kf.launch('continue')
        self.sc_kf.value = color.GRAY
        self.sc_kf.launch('continue')
        self.bg_kf.value = color.DEEPWHITE
        self.bg_kf.launch('continue')
        for t in self.title_text_fg_kf:
            t.value = color.GRAY
            t.launch('continue')

        if self.page.father is not None:
            self.page.leave()

sidebar_line = fantas.Label((2, u.HEIGHT), bg=color.GRAY, topright=(SIDEBAR_LEFT, 0))

structure = SidebarPage('电路结构')
analysis = SidebarPage('电路分析')
about = SidebarPage('关于')

def layout():
    sidebar_line.join(u.root)
    for i in range(len(SidebarPage.objects), 0, -1):
        SidebarPage.objects[i - 1].join(u.root)
    SidebarPage.objects[0].pop()


about_padding = about.page.rect.w / 4
about_lineheight = 36

i = fantas.Ui(u.images['icon'], midtop=(about.page.rect.w / 2, about_padding / 2))
i.anchor = "midtop"
i.size = (about_padding * 3, about_padding * 3)
i.join(about.page)

fantas.Text("三独立节点电路通用", u.fonts['shuhei'], textstyle.DARKBLUE_TITLE_3, midleft=(about_padding / 2, about_padding * 4)).join(about.page)
fantas.Text("正弦稳态电路分析器", u.fonts['shuhei'], textstyle.DARKBLUE_TITLE_3, midleft=(about_padding / 2, about_padding * 4 + about_lineheight)).join(about.page)
fantas.Text("V0.9.1", u.fonts['shuhei'], textstyle.DARKBLUE_TITLE_4, bottomright=(about.page.rect.w - about_padding / 2, about.page.kidgroup[-1].rect.bottom - 2)).join(about.page)
fantas.Label((about_padding * 3, 10), bg=color.DEEPWHITE, center=(about.page.rect.w / 2, about_padding * 4 + about_lineheight * 2)).join(about.page)
fantas.Text("山东大学 2024-2025 学年", u.fonts['shuhei'], textstyle.DARKBLUE_TITLE_4, midleft=(about_padding / 2, about_padding * 4 + about_lineheight * 3)).join(about.page)
fantas.Text("24级 电路课程设计作业", u.fonts['shuhei'], textstyle.DARKBLUE_TITLE_4, midleft=(about_padding / 2, about_padding * 4 + about_lineheight * 4)).join(about.page)
fantas.Label((about_padding * 3, 10), bg=color.DEEPWHITE, center=(about.page.rect.w / 2, about_padding * 4 + about_lineheight * 5)).join(about.page)
fantas.Text("小组成员：", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midleft=(about_padding / 2, about_padding * 4 + about_lineheight * 6)).join(about.page)
fantas.Text("白明惠", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_4, midleft=(about_padding / 2, about_padding * 4 + about_lineheight * 7)).join(about.page)
fantas.Text("李政锴", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_4, midleft=(about_padding / 2, about_padding * 4 + about_lineheight * 8)).join(about.page)
fantas.Text("吴浩哲", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_4, midleft=(about_padding / 2, about_padding * 4 + about_lineheight * 9)).join(about.page)
fantas.Text("周帆", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_4, midleft=(about.page.rect.w / 2, about_padding * 4 + about_lineheight * 7)).join(about.page)
fantas.Text("盛学萌", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_4, midleft=(about.page.rect.w / 2, about_padding * 4 + about_lineheight * 8)).join(about.page)
fantas.Label((about_padding * 3, 10), bg=color.DEEPWHITE, center=(about.page.rect.w / 2, about_padding * 4 + about_lineheight * 10)).join(about.page)
i = fantas.Ui(u.images['python'], midleft=(about_padding / 2, about_padding * 4 + about_lineheight * 11))
i.anchor = "midleft"
i.size = (about_lineheight, about_lineheight)
i.join(about.page)
fantas.Text("Python 3.12.10", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midright=(about_padding * 7 / 2, about_padding * 4 + about_lineheight * 11)).join(about.page)
i = fantas.Ui(u.images['pygame'], midleft=(about_padding / 2, about_padding * 4 + about_lineheight * 12 - 8))
i.anchor = "midleft"
i.size = (about_lineheight * 214 / 60, about_lineheight)
i.join(about.page)
fantas.Text("Pygame 2.6.1", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midright=(about_padding * 7 / 2, about_padding * 4 + about_lineheight * 12)).join(about.page)
i = fantas.Ui(u.images['numpy'], midleft=(about_padding / 2, about_padding * 4 + about_lineheight * 13))
i.anchor = "midleft"
i.size = (about_lineheight * 388 / 414, about_lineheight)
i.join(about.page)
fantas.Text("Numpy 2.2.5", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midright=(about_padding * 7 / 2, about_padding * 4 + about_lineheight * 13)).join(about.page)
fantas.Label((about_padding * 3, 10), bg=color.DEEPWHITE, center=(about.page.rect.w / 2, about_padding * 4 + about_lineheight * 14)).join(about.page)
fantas.IconText(chr(0xe85a), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3, midleft=(about_padding / 2, about_padding * 4 + about_lineheight * 15)).join(about.page)
fantas.WebURL("Github仓库", "https://github.com/EpochFIGHTER/Curcuit_homework", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midleft=(about_padding / 2 + about_lineheight, about_padding * 4 + about_lineheight * 15)).join(about.page)


PAGEWIDTH = u.WIDTH / 4
PAGEHEIGHT = u.HEIGHT
LISTPADDING = 20

class BranchListMouseWidget(fantas.MouseBase):
    SPEED = 120
    
    def __init__(self, ui):
        super().__init__(ui, 3)
    
    def mousescroll(self, x, y):
        if self.mouseon:
            value = min(max(self.ui.top_kf.value + y * self.SPEED, PAGEHEIGHT - self.ui.rect.h), 0)
            if self.ui.top_kf.value != value:
                self.ui.top_kf.value = value
                self.ui.top_kf.launch('continue')

class BranchList(fantas.Label):
    def __init__(self):
        super().__init__((PAGEWIDTH, LISTPADDING * 2))
        self.anchor = 'topleft'
        self.top_kf = fantas.RectKeyFrame(self, 'top', 0, 10, fantas.slower_curve)
        self.mousewidget = BranchListMouseWidget(self)
        self.mousewidget.apply_event()
        self.size_kf = fantas.LabelKeyFrame(self, 'size', (PAGEWIDTH, LISTPADDING * 2), 10, fantas.faster_curve)

    def append(self, node):
        super().append(node)
        self.add_height(node.MAX_HEIGHT + LISTPADDING)

    def remove(self, node):
        super().remove(node)
        self.add_height(- node.MAX_HEIGHT - LISTPADDING)

    def insert(self, node, index):
        super().insert(node, index)
        self.add_height(node.MAX_HEIGHT + LISTPADDING)
        if index < 0:
            index = len(self.kidgroup) + index
        self.move(index, node.size_kf.value[1] + LISTPADDING)

    def move(self, index, distance):
        for k in self.kidgroup[index:]:
            k.top_kf.value += distance
            k.top_kf.launch('continue')

    def add_height(self, height):
        if height > 0:
            self.size_kf.totalframe = 2
            self.size_kf.curve = fantas.faster_curve
        else:
            self.size_kf.totalframe = 20
            self.size_kf.curve = fantas.slower_curve
        self.size_kf.value = (self.size_kf.value[0], self.size_kf.value[1] + height)
        self.size_kf.launch('continue')

branch_list = BranchList()
branch_list.join(structure.page)

class ComponentList(fantas.Label):
    def __init__(self, **anchor):
        super().__init__((PAGEWIDTH - LISTPADDING * 2, 0), **anchor)
        self.anchor = 'topleft'
        self.top_kf = fantas.RectKeyFrame(self, 'top', 0, 10, fantas.slower_curve)
        # self.mousewidget = BranchListMouseWidget(self)
        # self.mousewidget.apply_event()
        self.size_kf = fantas.LabelKeyFrame(self, 'size', (PAGEWIDTH - LISTPADDING * 2, 0), 10, fantas.faster_curve)

    def append(self, node):
        super().append(node)
        self.add_height(node.MAX_HEIGHT + LISTPADDING)

    def remove(self, node):
        super().remove(node)
        self.add_height(- node.MAX_HEIGHT - LISTPADDING)
    
    def insert(self, node, index):
        super().insert(node, index)
        self.add_height(node.MAX_HEIGHT + LISTPADDING)
        if index < 0:
            index = len(self.kidgroup) + index
        self.move(index, node.size_kf.value[1] + LISTPADDING)
    
    def move(self, index, distance):
        for k in self.kidgroup[index:]:
            k.top_kf.value += distance
            k.top_kf.launch('continue')

    def add_height(self, height):
        if height > 0:
            self.size_kf.totalframe = 2
            self.size_kf.curve = fantas.faster_curve
        else:
            self.size_kf.totalframe = 20
            self.size_kf.curve = fantas.slower_curve
        self.size_kf.value = (self.size_kf.value[0], self.size_kf.value[1] + height)
        self.size_kf.launch('continue')

class AddBranchButtonMouseWidget(fantas.MouseBase):
    def __init__(self, ui):
        super().__init__(ui, 2)
        self.pressed_node = None
        self.released_node = None
        self.line : list = []

    def draw_branch(self):
        for i in self.ui.choose_nodes:
            i.style['fgcolor'] = color.GRAY
        if self.pressed_node is not None:
            self.ui.choose_nodes[self.pressed_node].style['fgcolor'] = color.DARKBLUE
        if self.released_node is not None:
            self.ui.choose_nodes[self.released_node].style['fgcolor'] = color.DARKBLUE
        for i in self.ui.choose_nodes:
            i.update_img()
        if self.line:
            for i in self.line:
                i.leave()
            self.line.clear()
        if self.pressed_node != self.released_node and self.pressed_node is not None and self.released_node is not None:
            if self.pressed_node > self.released_node:
                pressed_node, released_node = self.released_node, self.pressed_node
            else:
                pressed_node, released_node = self.pressed_node, self.released_node
            d = released_node - pressed_node
            if d == 1:
                l = fantas.Label((self.ui.rect.w / 4 - 16, 4), bg=color.DARKBLUE, center=(self.ui.rect.w / 4 * (pressed_node + 1), self.ui.MAX_HEIGHT * 3 / 2))
                l.join(self.ui)
                self.line.append(l)
            elif d > 1:
                l = fantas.Label((4, 16), bg=color.DARKBLUE, radius={'border_bottom_left_radius': 2, 'border_bottom_right_radius': 2}, midtop=(self.ui.rect.w / 8 * (pressed_node * 2 + 1), self.ui.MAX_HEIGHT * 3 / 2 + 8))
                l.join(self.ui)
                self.line.append(l)
                l = fantas.Label((4, 16), bg=color.DARKBLUE, radius={'border_bottom_left_radius': 2, 'border_bottom_right_radius': 2}, midtop=(self.ui.rect.w / 8 * (released_node * 2 + 1), self.ui.MAX_HEIGHT * 3 / 2 + 8))
                l.join(self.ui)
                self.line.append(l)
                l = fantas.Label((self.ui.rect.w / 4 * d, 4), bg=color.DARKBLUE, radius={'border_bottom_left_radius': 2, 'border_bottom_right_radius': 2}, midleft=(self.ui.rect.w / 8 * (pressed_node * 2 + 1), self.ui.MAX_HEIGHT * 3 / 2 + 24))
                l.join(self.ui)
                self.line.append(l)
            self.ui.add_text.text = f"n{nodes[pressed_node].num} --- n{nodes[released_node].num}"
            self.ui.add_text.update_img()
            return
        self.ui.add_text.text = "选择支路节点"
        self.ui.add_text.update_img()

    def mousepress(self, pos, button):
        if button == pygame.BUTTON_LEFT and self.ui.status == 1:
            if not self.mouseon:
                self.ui.hide_choose_branch()
            elif self.ui.MAX_HEIGHT < pos[1] - self.ui.rect.top < self.ui.MAX_HEIGHT * 2:
                i = int((pos[0] - self.ui.rect.left) / (self.ui.rect.w / 4))
                if 0 <= i < 4:
                    self.pressed_node = i
                    self.draw_branch()

    def mousemove(self, pos):
        if self.ui.status == 1 and self.pressed_node is not None:
            i = int((pos[0] - self.ui.rect.left) / (self.ui.rect.w / 4))
            if  0 <= i < 4 and i != self.released_node:
                self.released_node = i
                self.draw_branch()

    def mouserelease(self, pos, button):
        if button == pygame.BUTTON_LEFT and self.ui.status == 1:
            if self.pressed_node is None and self.released_node is None:
                return
            if self.pressed_node is not None and self.released_node is not None:
                if self.pressed_node > self.released_node:
                    pressed_node, released_node = self.released_node, self.pressed_node
                else:
                    pressed_node, released_node = self.pressed_node, self.released_node
                if pressed_node != released_node:
                    self.ui.add_choose_node(pressed_node, released_node)
            if self.pressed_node is not None:
                self.pressed_node = None
            if self.released_node is not None:
                self.released_node = None
            self.draw_branch()

class AddBranchButton(fantas.SmoothColorButton):
    MAX_HEIGHT = 80
    BG = color.LIGHTGREEN

    def __init__(self, **anchor):
        super().__init__((PAGEWIDTH - LISTPADDING * 2, self.MAX_HEIGHT), buttonstyle.branch_list_button_style, 2, radius={'border_radius': 16}, **anchor)
        self.anchor = 'midtop'
        self.bind(self.show_choose_branch)
        self.banned_mousewidget = AddBranchButtonMouseWidget(self)
        self.status = 0
        
        self.add_icon = fantas.IconText(chr(0xe620), u.fonts['iconfont'], textstyle.GRAY_TITLE_3, center=(self.rect.w / 2, self.rect.h / 2))
        self.add_icon.join(self)
        self.add_text = fantas.Text("选择支路节点", u.fonts['deyi'], textstyle.GRAY_TITLE_3, center=(self.rect.w / 2, self.rect.h / 2))
        self.choose_nodes = []
        for i in range(4):
            self.choose_nodes.append(fantas.IconText(chr(0xe6b5), u.fonts['iconfont'], dict(textstyle.GRAY_TITLE_3), center=(self.rect.w / 8 * (i * 2 + 1), self.rect.h / 2 * 3)))

        self.size_kf = fantas.LabelKeyFrame(self, 'size', (PAGEWIDTH - LISTPADDING * 2, self.MAX_HEIGHT), 10, fantas.harmonic_curve)
        self.top_kf = fantas.RectKeyFrame(self, 'top', self.rect.top, 10, fantas.harmonic_curve)

    def add_choose_node(self, node1, node2):
        BranchUi(node1, node2)
        self.hide_choose_branch()
        change_data()

    def show_choose_branch(self):
        self.ban()
        self.status = 1
        self.banned_mousewidget.mouseon = True
        self.size_kf.value = (PAGEWIDTH - LISTPADDING * 2, self.MAX_HEIGHT * 2)
        self.size_kf.launch('continue')
        self.add_icon.leave()
        self.add_text.join(self)
        for i in self.choose_nodes:
            i.join(self)
        branch_list.add_height(self.MAX_HEIGHT)

    def hide_choose_branch(self):
        self.status = 0
        self.recover()
        self.size_kf.value = (PAGEWIDTH - LISTPADDING * 2, self.MAX_HEIGHT)
        self.size_kf.launch('continue')
        self.add_icon.join(self)
        self.add_text.leave()
        for i in self.choose_nodes:
            i.leave()
        branch_list.add_height(-self.MAX_HEIGHT)

    def ban(self):
        super().ban()
        self.banned_mousewidget.apply_event()

    def recover(self):
        super().recover()
        self.banned_mousewidget.cancel_event()

add_branch_button = AddBranchButton(midtop=(PAGEWIDTH / 2, LISTPADDING))
add_branch_button.join(branch_list)

class BranchUi(fantas.Label):
    INIT_HEIGHT = 80
    MAX_HEIGHT = INIT_HEIGHT
    PADDING = 10

    def __init__(self, node1, node2):
        super().__init__((PAGEWIDTH - LISTPADDING * 2, 0), 2, color.LIGHTGREEN, color.GRAY, radius={'border_radius': 16}, midtop=(PAGEWIDTH / 2, add_branch_button.rect.top))
        self.anchor = 'midtop'

        self.size_kf = fantas.LabelKeyFrame(self, 'size', (PAGEWIDTH - LISTPADDING * 2, self.INIT_HEIGHT), 10, fantas.harmonic_curve)
        self.top_kf = fantas.RectKeyFrame(self, 'top', self.rect.top, 10, fantas.harmonic_curve)
        self.size_kf.launch('continue')

        self.join_to(branch_list, -1)

        node1 = nodes[node1]
        node2 = nodes[node2]
        self.branch = ElectricalBranch(node1, node2)
        viewbox.diagram_box.update()

        self.unfold_button = fantas.SmoothColorButton((self.INIT_HEIGHT - self.PADDING * 2, self.INIT_HEIGHT - self.PADDING * 2), buttonstyle.common_button_style, 2, radius={'border_radius': 16}, topleft=(self.PADDING, self.PADDING))
        self.unfold_button.join(self)
        self.unfold_button.bind(self.unfold)
        self.unfold_icon = fantas.IconText(chr(0xe60e), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3, center=(self.unfold_button.rect.w / 2, self.unfold_button.rect.h / 2))
        self.unfold_icon.angle = 90
        self.unfold_icon.join(self.unfold_button)
        self.unfold_icon_angle_kf = fantas.UiKeyFrame(self.unfold_icon, 'angle',90, 10, fantas.harmonic_curve)

        self.title_text = fantas.Text(f"n{node1.num} --- n{node2.num}", u.fonts['shuhei'], textstyle.DARKBLUE_TITLE_3, center=(self.rect.w / 2, self.unfold_button.rect.centery))
        self.title_text.join(self)

        self.delete_button = fantas.SmoothColorButton((self.INIT_HEIGHT - self.PADDING * 2, self.INIT_HEIGHT - self.PADDING * 2), buttonstyle.warn_button_style, 2, radius={'border_radius': 16}, topright=(self.rect.w - self.PADDING, self.PADDING))
        self.delete_button.join(self)
        self.delete_button.bind(self.delete)
        self.delete_icon = fantas.IconText(chr(0xe66b), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3, center=(self.delete_button.rect.w / 2, self.delete_button.rect.h / 2))
        self.delete_icon.join(self.delete_button)

        self.component_list = ComponentList(midtop=(self.rect.w / 2, self.INIT_HEIGHT))
        self.add_component_button = AddComponentButton(self, midtop=(self.rect.w / 2, self.PADDING))
        self.add_component_button.join(self.component_list)
        self.unfold()

    def unfold(self):
        self.component_list.join(self)
        self.size_kf.value = (PAGEWIDTH - LISTPADDING * 2, self.INIT_HEIGHT + self.component_list.size_kf.value[1] + self.PADDING * 2)
        self.size_kf.launch('continue')
        branch_list.add_height(self.component_list.size_kf.value[1] + self.PADDING * 2)
        branch_list.move(self.get_index() + 1, self.component_list.size_kf.value[1] + self.PADDING * 2)
        self.unfold_button.bind(self.fold)
        self.unfold_icon_angle_kf.value = 0
        self.unfold_icon_angle_kf.launch('continue')

    def fold(self):
        self.size_kf.bind_endupwith(self.after_fold)
        self.size_kf.value = (self.size_kf.value[0], self.size_kf.value[1] - self.component_list.size_kf.value[1] - self.PADDING * 2)
        self.size_kf.launch('continue')
        branch_list.add_height(-self.component_list.size_kf.value[1] - self.PADDING * 2)
        branch_list.move(self.get_index() + 1, -self.component_list.size_kf.value[1] - self.PADDING * 2)
        self.unfold_button.bind(self.unfold)
        self.unfold_icon_angle_kf.value = 90
        self.unfold_icon_angle_kf.launch('continue')

    def after_fold(self):
        self.component_list.leave()
        self.size_kf.bind_endupwith(None)

    def delete(self):
        branch_list.add_height(self.MAX_HEIGHT - self.size_kf.value[1])
        branch_list.move(self.get_index() + 1, -self.size_kf.value[1] - LISTPADDING)
        self.leave()
        self.branch.node_left.branches[self.branch.node_right].remove(self.branch)
        self.branch.node_right.branches[self.branch.node_left].remove(self.branch)
        viewbox.diagram_box.update()
        change_data()

class AddComponentMouseWidget(fantas.MouseBase):
    def __init__(self, ui):
        super().__init__(ui, 2)
    
    def mousepress(self, pos, button):
        if button == pygame.BUTTON_LEFT and self.ui.status == 1:
            if not self.mouseon:
                self.ui.hide_choose_component()        

class AddComponentButton(fantas.SmoothColorButton):
    MAX_HEIGHT = 80
    BG = color.LIGHTGREEN

    def __init__(self, branchui, **anchor):
        super().__init__((PAGEWIDTH - LISTPADDING * 4, self.MAX_HEIGHT), buttonstyle.branch_list_button_style, 2, radius={'border_radius': 16}, **anchor)
        self.anchor = 'midtop'
        self.bind(self.show_choose_component)
        self.banned_mousewidget = AddComponentMouseWidget(self)
        self.status = 0
        self.branchui = branchui
    
        self.add_icon = fantas.IconText(chr(0xe620), u.fonts['iconfont'], textstyle.GRAY_TITLE_3, center=(self.rect.w / 2, self.rect.h / 2))
        self.add_icon.join(self)
        self.add_text = fantas.Text("选择元件类型", u.fonts['deyi'], textstyle.GRAY_TITLE_3, center=(self.rect.w / 2, self.rect.h / 2))

        self.choose_components = []
        for i in range(8):
            self.choose_components.append(ChooseComponentButton(i, self.branchui, center=(self.rect.w / 16 * (i * 2 + 1), self.rect.h / 2 * 3)))

        self.size_kf = fantas.LabelKeyFrame(self, 'size', (PAGEWIDTH - LISTPADDING * 4, self.MAX_HEIGHT), 10, fantas.harmonic_curve)
        self.top_kf = fantas.RectKeyFrame(self, 'top', self.rect.top, 10, fantas.harmonic_curve)
    
    def show_choose_component(self):
        self.ban()
        self.status = 1
        self.banned_mousewidget.mouseon = True
        self.size_kf.value = (self.size_kf.value[0], self.size_kf.value[1] + self.MAX_HEIGHT)
        self.size_kf.launch('continue')
        self.add_icon.leave()
        self.add_text.join(self)
        for i in self.choose_components:
            i.join(self)
        self.branchui.component_list.add_height(self.MAX_HEIGHT)
        self.branchui.size_kf.value = (self.branchui.size_kf.value[0], self.branchui.size_kf.value[1] + self.MAX_HEIGHT)
        self.branchui.size_kf.launch('continue')
        branch_list.add_height(self.MAX_HEIGHT)
        branch_list.move(self.branchui.get_index() + 1, self.MAX_HEIGHT)

    def hide_choose_component(self):
        self.status = 0
        self.recover()
        self.size_kf.value = (self.size_kf.value[0], self.size_kf.value[1] - self.MAX_HEIGHT)
        self.size_kf.launch('continue')
        self.add_icon.join(self)
        self.add_text.leave()
        for i in self.choose_components:
            i.leave()
        self.branchui.component_list.add_height(-self.MAX_HEIGHT)
        self.branchui.size_kf.value = (self.branchui.size_kf.value[0], self.branchui.size_kf.value[1] - self.MAX_HEIGHT)
        self.branchui.size_kf.launch('continue')
        branch_list.add_height(-self.MAX_HEIGHT)
        branch_list.move(self.branchui.get_index() + 1, -self.MAX_HEIGHT)

    def ban(self):
        super().ban()
        self.banned_mousewidget.apply_event()

    def recover(self):
        super().recover()
        self.banned_mousewidget.cancel_event()

class ChooseComponentButtonMouseWidget(fantas.ColorButtonMouseWidget):
    def mousein(self):
        super().mousein()
        self.ui.father.add_text.text = COMPONENT_NAME[self.ui.num]
        self.ui.father.add_text.update_img()
    
    def mouseout(self):
        super().mouseout()
        self.ui.father.add_text.text = "选择元件类型"
        self.ui.father.add_text.update_img()

IMG_NAME = ('R', 'C', 'L', 'Z', 'U', 'I', 'kU', 'kI')
COMPONENT_NAME = ('电阻', '电容', '电感', '通用阻抗', '独立电压源', '独立电流源', '受控电压源', '受控电流源')
COMPONENT_CLASS = (Resistor, Capacitor, Inductor, Impedance, IndependentVoltageSource, IndependentCurrentSource, DependentVoltageSource, DependentCurrentSource)
for i in IMG_NAME:
    img = pygame.Surface((180, 80), pygame.SRCALPHA)
    img.fill((255, 255, 255, 255))
    img.blit(u.images[i], (0, 0), special_flags=pygame.BLEND_RGB_SUB)
    img_ = pygame.Surface((180, 80), pygame.SRCALPHA)
    img_.fill((0, 0, 0, 255))
    img_.blit(u.images[i], (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    img.blit(img_, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    u.images[f"DARK_{i}"] = img

class ChooseComponentButton(fantas.SmoothColorButton):
    SIZE = 40

    def __init__(self, num, branchui, **kwargs):
        super().__init__((self.SIZE, self.SIZE), buttonstyle.common_button_style, 2, ChooseComponentButtonMouseWidget, **kwargs)
        self.num = num
        self.branchui = branchui
        if color.IS_DARKMODE:
            self.icon = fantas.Ui(u.images[f"DARK_{IMG_NAME[num]}"], center=(self.rect.w / 2, self.rect.h / 2))
        else:
            self.icon = fantas.Ui(u.images[IMG_NAME[num]], center=(self.rect.w / 2, self.rect.h / 2))
        self.icon.size = (self.SIZE, self.SIZE * 80 / 180)
        self.icon.join(self)
        self.apply_size()
        self.bind(self.add_component)

    def add_component(self):
        c = COMPONENTUI_CLASS[self.num](self.branchui, self.num, topleft=(LISTPADDING, self.branchui.add_component_button.rect.top))
        c.join_to(self.branchui.component_list, -1)
        c.branchui.size_kf.value = (c.branchui.size_kf.value[0], c.branchui.size_kf.value[1] + c.MAX_HEIGHT + LISTPADDING)
        c.branchui.size_kf.launch('continue')
        self.father.hide_choose_component()
        branch_list.add_height(c.MAX_HEIGHT + LISTPADDING)
        branch_list.move(self.branchui.get_index() + 1, c.MAX_HEIGHT + LISTPADDING)
        change_data()

LEFT_FLAG_POS = (30, 20)
RIGHT_FLAG_POS = (130, 20)
ARROW_POS = (80, 80)

def change_data():
    global caculated_flag
    viewbox.diagram_box.update()
    if caculated_flag:
        caculated_flag = False
        calculate_button.title_text.text = "求解电路"
        calculate_button.title_text.update_img()
        calculate_button.title_text_color_kf.value = color.DARKBLUE
        calculate_button.title_text_color_kf.launch('continue')
        calculate_button.recover()

class ComponentUiInputWidget(NumberInputWidget):
    def stop_input(self):
        super().stop_input()
        self.ui.father.set_data()
        change_data()

class ComponentUnitSwitchButton(UnitSwitchButton):
    def switch(self):
        super().switch()
        self.father.set_data()
        change_data()

class ComponentUiIconMouseWidget(fantas.MouseBase):
    def __init__(self, ui):
        super().__init__(ui, 1)
    
    def mousepress(self, pos, button):
        if button == pygame.BUTTON_LEFT == self.mousedown:
            if (pos[1] - self.ui.rect.top) < self.ui.rect.h / 2:
                self.ui.father.switch_Vref()
                viewbox.diagram_box.update()
            else:
                self.ui.father.switch_Iref()
                viewbox.diagram_box.update()

class ComponentUi(fantas.Label):
    MAX_HEIGHT = 160

    def __init__(self, branchui, num, **anchor):
        super().__init__((PAGEWIDTH - LISTPADDING * 4, 0), 2, color.LIGHTGREEN, color.GRAY, radius={'border_radius': 16}, **anchor)
        self.anchor = 'midtop'
        self.branchui = branchui
        self.num = num

        self.size_kf = fantas.LabelKeyFrame(self, 'size', (PAGEWIDTH - LISTPADDING * 4, self.MAX_HEIGHT), 10, fantas.harmonic_curve)
        self.top_kf = fantas.RectKeyFrame(self, 'top', self.rect.top, 10, fantas.harmonic_curve)
        self.size_kf.launch('continue')

        self.component = COMPONENT_CLASS[num](self.branchui.branch)
        self.branchui.branch.append(self.component)
        viewbox.diagram_box.update()

        if color.IS_DARKMODE:
            self.icon = fantas.Ui(u.images[f"DARK_{IMG_NAME[num]}"], center=(self.MAX_HEIGHT / 2, self.MAX_HEIGHT / 4))
        else:
            self.icon = fantas.Ui(u.images[IMG_NAME[num]], center=(self.MAX_HEIGHT / 2, self.MAX_HEIGHT / 4))
        self.icon.size = (self.MAX_HEIGHT, self.MAX_HEIGHT * 80 / 180)
        self.icon.apply_size()
        self.icon.join(self)
        self.icon_name = fantas.Text(f"{self.component.prefix}{self.component.num}", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, center=(self.MAX_HEIGHT / 2, self.MAX_HEIGHT * 3 / 4))
        self.icon_name.join(self)

        self.moveup_button = fantas.SmoothColorButton((self.MAX_HEIGHT / 4, self.MAX_HEIGHT / 4), buttonstyle.common_button_style, 2, radius={'border_radius': self.MAX_HEIGHT // 8}, center=(self.size_kf.value[0] - self.MAX_HEIGHT / 4, self.MAX_HEIGHT / 5))
        self.moveup_button.bind(self.moveup)
        self.moveup_button.join(self)
        self.moveup_icon = fantas.IconText(chr(0xe60e), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3, center=(self.moveup_button.rect.w / 2, self.moveup_button.rect.h / 2))
        self.moveup_icon.angle = 180
        self.moveup_icon.join(self.moveup_button)
        self.movedown_button = fantas.SmoothColorButton((self.MAX_HEIGHT / 4, self.MAX_HEIGHT / 4), buttonstyle.common_button_style, 2, radius={'border_radius': self.MAX_HEIGHT // 8}, center=(self.size_kf.value[0] - self.MAX_HEIGHT / 4, self.MAX_HEIGHT * 4 / 5))
        self.movedown_button.bind(self.movedown)
        self.movedown_button.join(self)
        self.movedown_icon = fantas.IconText(chr(0xe60e), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3, center=(self.movedown_button.rect.w / 2, self.movedown_button.rect.h / 2))
        self.movedown_icon.join(self.movedown_button)
        self.delete_button = fantas.SmoothColorButton((self.MAX_HEIGHT / 4, self.MAX_HEIGHT / 4), buttonstyle.warn_button_style, 2, radius={'border_radius': self.MAX_HEIGHT // 8}, center=(self.size_kf.value[0] - self.MAX_HEIGHT / 4, self.MAX_HEIGHT / 2))
        self.delete_button.bind(self.delete)
        self.delete_button.join(self)
        self.delete_icon = fantas.IconText(chr(0xe66b), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_4, center=(self.delete_button.rect.w / 2 - 1, self.delete_button.rect.h / 2))
        self.delete_icon.join(self.delete_button)

        self.posi_flag = fantas.Text("+", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, center=LEFT_FLAG_POS)
        self.posi_flag.join(self)
        self.nega_flag = fantas.Text("-", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, center=RIGHT_FLAG_POS)
        self.nega_flag.join(self)

        self.posi_pos_kf = fantas.RectKeyFrame(self.posi_flag, 'center', LEFT_FLAG_POS, 10, fantas.harmonic_curve)
        self.nega_pos_kf = fantas.RectKeyFrame(self.nega_flag, 'center', RIGHT_FLAG_POS, 10, fantas.harmonic_curve)

        self.arrow = fantas.IconText(chr(0xe602), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_2, center=ARROW_POS)
        self.arrow.join(self)
        self.arrow_angle_kf = fantas.UiKeyFrame(self.arrow, 'angle', 0, 10, fantas.harmonic_curve)

        ComponentUiIconMouseWidget(self.icon).apply_event()

    def moveup(self):
        index = self.component.get_index()
        if index == 0:
            return
        self.component.move_left()
        viewbox.diagram_box.update()
        self.father.kidgroup[index - 1], self.father.kidgroup[index] = self.father.kidgroup[index], self.father.kidgroup[index - 1]
        self.father.kidgroup[index - 1].top_kf.value, self.father.kidgroup[index].top_kf.value = self.father.kidgroup[index].top_kf.value, self.father.kidgroup[index - 1].top_kf.value
        self.father.kidgroup[index - 1].top_kf.launch('continue')
        self.father.kidgroup[index].top_kf.launch('continue')
        change_data()

    def movedown(self):
        index = self.component.get_index()
        if index == len(self.component.branch) - 1:
            return
        self.component.move_right()
        viewbox.diagram_box.update()
        self.father.kidgroup[index + 1], self.father.kidgroup[index] = self.father.kidgroup[index], self.father.kidgroup[index + 1]
        self.father.kidgroup[index + 1].top_kf.value, self.father.kidgroup[index].top_kf.value = self.father.kidgroup[index].top_kf.value, self.father.kidgroup[index + 1].top_kf.value
        self.father.kidgroup[index + 1].top_kf.launch('continue')
        self.father.kidgroup[index].top_kf.launch('continue')
        change_data()

    def delete(self):
        self.father.add_height(self.MAX_HEIGHT - self.size_kf.value[1])
        self.father.move(self.get_index() + 1, -self.size_kf.value[1] - LISTPADDING)
        self.leave()
        self.component.branch.remove(self.component)
        viewbox.diagram_box.update()
        self.branchui.size_kf.value = (self.branchui.size_kf.value[0], self.branchui.size_kf.value[1] - self.MAX_HEIGHT - LISTPADDING)
        self.branchui.size_kf.launch('continue')
        branch_list.add_height(-self.MAX_HEIGHT - LISTPADDING)
        branch_list.move(self.branchui.get_index() + 1, -self.MAX_HEIGHT - LISTPADDING)
        change_data()

    def switch_Vref(self):
        self.component.Vref = not self.component.Vref
        if self.component.Vref:
            self.posi_pos_kf.value = LEFT_FLAG_POS
            self.nega_pos_kf.value = RIGHT_FLAG_POS
        else:
            self.posi_pos_kf.value = RIGHT_FLAG_POS
            self.nega_pos_kf.value = LEFT_FLAG_POS
        self.posi_pos_kf.launch('continue')
        self.nega_pos_kf.launch('continue')

    def switch_Iref(self):
        self.component.Iref = not self.component.Iref
        if self.component.Iref:
            self.arrow_angle_kf.value = 0
        else:
            self.arrow_angle_kf.value = 180
        self.arrow_angle_kf.launch('continue')
    
    def set_data(self):
        return False

class ResistorUi(ComponentUi):
    def __init__(self, branchui, num, **anchor):
        super().__init__(branchui, num, **anchor)

        self.value_input_box = fantas.InputLine((120, 40), u.fonts['deyi'], inputstyle.small_style, textstyle.DARKBLUE_TITLE_4, "电阻值", 32, ComponentUiInputWidget, bd=2, sc=color.GRAY, bg=color.LIGHTWHITE, radius={ 'border_radius': 12 }, midleft=(self.MAX_HEIGHT, self.MAX_HEIGHT / 2))
        self.value_input_box.join(self)
        self.value_unit_box = ComponentUnitSwitchButton(Core.R_table, 1, midleft=(self.value_input_box.rect.right + 10, self.value_input_box.rect.centery))
        self.value_unit_box.join(self)
    
    def set_data(self):
        r = self.value_input_box.inputwidget.get_number()
        unit = Core.R_k[self.value_unit_box.unit]
        if r is None:
            return False
        self.component.R = r / unit
        return True


class CapacitorUi(ComponentUi):
    def __init__(self, branchui, num, **anchor):
        super().__init__(branchui, num, **anchor)

        self.value_input_box = fantas.InputLine((120, 40), u.fonts['deyi'], inputstyle.small_style, textstyle.DARKBLUE_TITLE_4, "电容值", 32, ComponentUiInputWidget, bd=2, sc=color.GRAY, bg=color.LIGHTWHITE, radius={ 'border_radius': 12 }, midleft=(self.MAX_HEIGHT, self.MAX_HEIGHT / 2))
        self.value_input_box.join(self)
        self.value_unit_box = ComponentUnitSwitchButton(Core.C_table, 2, midleft=(self.value_input_box.rect.right + 10, self.value_input_box.rect.centery))
        self.value_unit_box.join(self)
    
    def set_data(self):
        c = self.value_input_box.inputwidget.get_number()
        unit = Core.C_k[self.value_unit_box.unit]
        if c is None:
            return False
        self.component.C = c / unit
        return True

class InductorUi(ComponentUi):
    def __init__(self, branchui, num, **anchor):
        super().__init__(branchui, num, **anchor)

        self.value_input_box = fantas.InputLine((120, 40), u.fonts['deyi'], inputstyle.small_style, textstyle.DARKBLUE_TITLE_4, "电感值", 32, ComponentUiInputWidget, bd=2, sc=color.GRAY, bg=color.LIGHTWHITE, radius={ 'border_radius': 12 }, midleft=(self.MAX_HEIGHT, self.MAX_HEIGHT / 2))
        self.value_input_box.join(self)
        self.value_unit_box = ComponentUnitSwitchButton(Core.L_table, 1, midleft=(self.value_input_box.rect.right + 10, self.value_input_box.rect.centery))
        self.value_unit_box.join(self)

    def set_data(self):
        l = self.value_input_box.inputwidget.get_number()
        unit = Core.L_k[self.value_unit_box.unit]
        if l is None:
            return False
        self.component.L = l / unit
        return True

class ImpedanceUi(ComponentUi):
    def __init__(self, branchui, num, **anchor):
        super().__init__(branchui, num, **anchor)

        self.value_input_box = fantas.InputLine((120, 40), u.fonts['deyi'], inputstyle.small_style, textstyle.DARKBLUE_TITLE_4, "阻抗值", 32, ComponentUiInputWidget, bd=2, sc=color.GRAY, bg=color.LIGHTWHITE, radius={ 'border_radius': 12 }, midleft=(self.MAX_HEIGHT, self.MAX_HEIGHT / 3))
        self.value_input_box.join(self)
        self.value_unit_box = ComponentUnitSwitchButton(Core.R_table, 1, midleft=(self.value_input_box.rect.right + 10, self.value_input_box.rect.centery))
        self.value_unit_box.join(self)
        self.angle_input_box = fantas.InputLine((100, 40), u.fonts['deyi'], inputstyle.small_style, textstyle.DARKBLUE_TITLE_4, "阻抗角", 32, ComponentUiInputWidget, bd=2, sc=color.GRAY, bg=color.LIGHTWHITE, radius={ 'border_radius': 12 }, midleft=(self.MAX_HEIGHT + 20, self.MAX_HEIGHT * 2 / 3))
        self.angle_input_box.join(self)
        fantas.IconText(chr(0xe619), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3, midright=(self.angle_input_box.rect.left - 8, self.angle_input_box.rect.centery)).join(self)
        fantas.Text("°", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midleft=(self.angle_input_box.rect.right + 10, self.angle_input_box.rect.centery)).join(self)
    
    def set_data(self):
        z = self.value_input_box.inputwidget.get_number()
        unit = Core.R_k[self.value_unit_box.unit]
        if z is None:
            return False
        a = self.angle_input_box.inputwidget.get_number()
        if a is None:
            return False
        self.component.Z = cmath.rect(z / unit, math.radians(a))
        return True

class IndependentVoltageSourceUi(ComponentUi):
    def __init__(self, branchui, num, **anchor):
        super().__init__(branchui, num, **anchor)
        self.arrow.rect.centery += 10

        self.value_input_box = fantas.InputLine((120, 40), u.fonts['deyi'], inputstyle.small_style, textstyle.DARKBLUE_TITLE_4, "电压值", 32, ComponentUiInputWidget, bd=2, sc=color.GRAY, bg=color.LIGHTWHITE, radius={ 'border_radius': 12 }, midleft=(self.MAX_HEIGHT, self.MAX_HEIGHT / 3))
        self.value_input_box.join(self)
        self.value_unit_box = ComponentUnitSwitchButton(Core.V_table, 1, midleft=(self.value_input_box.rect.right + 10, self.value_input_box.rect.centery))
        self.value_unit_box.join(self)
        self.angle_input_box = fantas.InputLine((100, 40), u.fonts['deyi'], inputstyle.small_style, textstyle.DARKBLUE_TITLE_4, "相位角", 32, ComponentUiInputWidget, bd=2, sc=color.GRAY, bg=color.LIGHTWHITE, radius={ 'border_radius': 12 }, midleft=(self.MAX_HEIGHT + 20, self.MAX_HEIGHT * 2 / 3))
        self.angle_input_box.join(self)
        fantas.IconText(chr(0xe619), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3, midright=(self.angle_input_box.rect.left - 8, self.angle_input_box.rect.centery)).join(self)
        fantas.Text("°", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midleft=(self.angle_input_box.rect.right + 10, self.angle_input_box.rect.centery)).join(self)
    
    def set_data(self):
        v = self.value_input_box.inputwidget.get_number()
        unit = Core.V_k[self.value_unit_box.unit]
        if v is None:
            return False
        a = self.angle_input_box.inputwidget.get_number()
        if a is None:
            return False
        self.component.U = cmath.rect((v if self.component.Vref else -v) / unit, math.radians(a))
        return True

class IndependentCurrentSourceUi(ComponentUi):
    def __init__(self, branchui, num, **anchor):
        super().__init__(branchui, num, **anchor)
        self.arrow.rect.centery += 10

        self.value_input_box = fantas.InputLine((120, 40), u.fonts['deyi'], inputstyle.small_style, textstyle.DARKBLUE_TITLE_4, "电流值", 32, ComponentUiInputWidget, bd=2, sc=color.GRAY, bg=color.LIGHTWHITE, radius={ 'border_radius': 12 }, midleft=(self.MAX_HEIGHT, self.MAX_HEIGHT / 3))
        self.value_input_box.join(self)
        self.value_unit_box = ComponentUnitSwitchButton(Core.I_table, 2, midleft=(self.value_input_box.rect.right + 10, self.value_input_box.rect.centery))
        self.value_unit_box.join(self)
        self.angle_input_box = fantas.InputLine((100, 40), u.fonts['deyi'], inputstyle.small_style, textstyle.DARKBLUE_TITLE_4, "相位角", 32, ComponentUiInputWidget, bd=2, sc=color.GRAY, bg=color.LIGHTWHITE, radius={ 'border_radius': 12 }, midleft=(self.MAX_HEIGHT + 20, self.MAX_HEIGHT * 2 / 3))
        self.angle_input_box.join(self)
        fantas.IconText(chr(0xe619), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3, midright=(self.angle_input_box.rect.left - 8, self.angle_input_box.rect.centery)).join(self)
        fantas.Text("°", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midleft=(self.angle_input_box.rect.right + 10, self.angle_input_box.rect.centery)).join(self)
    
    def set_data(self):
        i = self.value_input_box.inputwidget.get_number()
        unit = Core.I_k[self.value_unit_box.unit]
        if i is None:
            return False
        a = self.angle_input_box.inputwidget.get_number()
        if a is None:
            return False
        self.component.I = cmath.rect((i if self.component.Iref else -i) / unit, math.radians(a))
        return True

VA_table = ("U", "I")

class ControlComponentInputWidget(fantas.InputLineWidget):
    def stop_input(self):
        super().stop_input()
        if Core.COMPONENT_DICT.get(self.ui.text.text) is None:
            self.ui.clear()
        self.ui.father.set_data()
        change_data()

class DependentVoltageSourceUi(ComponentUi):
    def __init__(self, branchui, num, **anchor):
        super().__init__(branchui, num, **anchor)

        self.value_input_box = fantas.InputLine((100, 40), u.fonts['deyi'], inputstyle.small_style, textstyle.DARKBLUE_TITLE_4, "系数", 32, ComponentUiInputWidget, bd=2, sc=color.GRAY, bg=color.LIGHTWHITE, radius={ 'border_radius': 12 }, midleft=(self.MAX_HEIGHT, self.MAX_HEIGHT * 2 / 3))
        self.value_input_box.join(self)
        self.value_unit_box = ComponentUnitSwitchButton(VA_table, 0, midleft=(self.value_input_box.rect.right + 10, self.value_input_box.rect.centery))
        self.value_unit_box.join(self)

        fantas.Text("控制元件", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_4, midleft=(self.MAX_HEIGHT, self.MAX_HEIGHT / 3)).join(self)
        self.control_component_input_box = fantas.InputLine((80, 40), u.fonts['deyi'], inputstyle.small_style, textstyle.DARKBLUE_TITLE_4, maxinput=8, inputwidget=ControlComponentInputWidget, bd=2, sc=color.GRAY, bg=color.LIGHTWHITE, radius={ 'border_radius': 12 }, midleft=(self.MAX_HEIGHT * 1.5, self.MAX_HEIGHT / 3))
        self.control_component_input_box.join(self)
    
    def set_data(self):
        self.component.controler = Core.COMPONENT_DICT.get(self.control_component_input_box.text.text)
        self.component.value = VA_table[self.value_unit_box.unit]
        if self.component.controler is None:
            return False
        k = self.value_input_box.inputwidget.get_number()
        if k is None:
            return False
        self.component.k = k
        return True

class DependentCurrentSourceUi(ComponentUi):
    def __init__(self, branchui, num, **anchor):
        super().__init__(branchui, num, **anchor)

        self.value_input_box = fantas.InputLine((100, 40), u.fonts['deyi'], inputstyle.small_style, textstyle.DARKBLUE_TITLE_4, "系数", 32, ComponentUiInputWidget, bd=2, sc=color.GRAY, bg=color.LIGHTWHITE, radius={ 'border_radius': 12 }, midleft=(self.MAX_HEIGHT, self.MAX_HEIGHT * 2 / 3))
        self.value_input_box.join(self)
        self.value_unit_box = ComponentUnitSwitchButton(VA_table, 0, midleft=(self.value_input_box.rect.right + 10, self.value_input_box.rect.centery))
        self.value_unit_box.join(self)

        fantas.Text("控制元件", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_4, midleft=(self.MAX_HEIGHT, self.MAX_HEIGHT / 3)).join(self)
        self.control_component_input_box = fantas.InputLine((80, 40), u.fonts['deyi'], inputstyle.small_style, textstyle.DARKBLUE_TITLE_4, maxinput=8, inputwidget=ControlComponentInputWidget, bd=2, sc=color.GRAY, bg=color.LIGHTWHITE, radius={ 'border_radius': 12 }, midleft=(self.MAX_HEIGHT * 1.5, self.MAX_HEIGHT / 3))
        self.control_component_input_box.join(self)
    
    def set_data(self):
        self.component.controler = Core.COMPONENT_DICT.get(self.control_component_input_box.text.text)
        self.component.value = VA_table[self.value_unit_box.unit]
        if self.component.controler is None:
            return False
        k = self.value_input_box.inputwidget.get_number()
        if k is None:
            return False
        self.component.k = k
        return True

COMPONENTUI_CLASS = (ResistorUi, CapacitorUi, InductorUi, ImpedanceUi, IndependentVoltageSourceUi, IndependentCurrentSourceUi, DependentVoltageSourceUi, DependentCurrentSourceUi)
caculated_flag = False

SOLVE_METHODS = ('auto', 'lstsq', 'pinv', 'direct')
class CalculateButton(fantas.SmoothColorButton):
    HEIGHT = 120
    LINEHEIGHT = 48
    PADDING = 20

    def __init__(self, **anchor):
        super().__init__((PAGEWIDTH - LISTPADDING * 2, self.HEIGHT), buttonstyle.impoortant_button_style, 2, radius={'border_radius': 16}, **anchor)
        self.anchor = "midtop"
        self.method_num = 0
        self.bind(self.calculate)

        self.title_text = fantas.Text("求解电路", u.fonts['deyi'], dict(textstyle.DARKBLUE_TITLE_2), center=(self.rect.w / 2, self.rect.h / 2))
        self.title_text.join(self)
        self.title_text_color_kf = fantas.TextKeyFrame(self.title_text, 'fgcolor', color.FAKEWHITE, 10, fantas.harmonic_curve)

        self.load_icon = fantas.IconText(chr(0xe61d), u.fonts['iconfont'], textstyle.FAKEWHITE_TITLE_3, center=(self.rect.h / 2, self.rect.h / 2))
        self.load_icon_angle_kf = fantas.UiKeyFrame(self.load_icon, 'angle', -360, 48, fantas.harmonic_curve)
        self.load_icon_angle_kf.bind_endupwith(self.load)

        self.size_kf = fantas.LabelKeyFrame(self, 'size', (PAGEWIDTH - LISTPADDING * 2, self.HEIGHT), 10, fantas.harmonic_curve)

        self.text_temp = []

    def calculate(self):
        f = viewbox.freq_inputline.inputwidget.get_number()
        if f is None:
            return
        Core.set_freq(f)
        for b in branch_list.kidgroup:
            if isinstance(b, BranchUi):
                for c in b.component_list.kidgroup:
                    if isinstance(c, ComponentUi):
                        if not c.set_data():
                            return
        self.ban()
        self.title_text_color_kf.value = color.FAKEWHITE
        self.title_text_color_kf.launch('continue')
        self.load_icon.angle = 0
        self.load_icon_angle_kf.launch('continue')
        self.size_kf.value = (self.size_kf.value[0], self.size_kf.value[1] + self.LINEHEIGHT)
        self.title_text.text = "正在计算电路..."
        self.title_text.update_img()
        self.load_icon.join(self)
        self.add_text(f">>> 尝试使用 {SOLVE_METHODS[0]} 方法求解")

    def load(self):
        global caculated_flag
        success, node_voltages, branch_currents = solve_circuit(nodes, solver_method=SOLVE_METHODS[self.method_num])
        if success:
            # print_circuit_solution(nodes, node_voltages, branch_currents)
            self.add_text(f">>> {SOLVE_METHODS[self.method_num]} 方法求解成功")
            self.title_text.text = "求解已完成！"
            self.title_text.update_img()
            self.load_icon.leave()
            caculated_flag = True
            fantas.Trigger(self.clear_text).launch(90)
            return
        else:
            self.add_text(f">>> {SOLVE_METHODS[self.method_num]} 方法求解失败")
            self.method_num += 1
            if self.method_num >= len(SOLVE_METHODS):
                self.method_num = 0
                self.add_text("")
                self.add_text(f">>> 请检查电路结构")
                self.title_text.text = "求解失败！"
                self.title_text.update_img()
                self.load_icon.leave()
                fantas.Trigger(self.clear_text).launch(90)
                return
            self.add_text("")
            self.add_text(f">>> 尝试使用 {SOLVE_METHODS[self.method_num]} 方法求解")
        self.load_icon.angle = 0
        self.load_icon_angle_kf.launch('continue')

    def add_text(self, text):
        self.size_kf.value = (self.size_kf.value[0], self.size_kf.value[1] + self.LINEHEIGHT)
        self.size_kf.launch('continue')
        t = fantas.Text(text, u.fonts['deyi'], textstyle.FAKEWHITE_TITLE_3, midleft=(self.PADDING, self.size_kf.value[1] - self.LINEHEIGHT))
        t.alpha = 0
        t.join(self)
        self.text_temp.append(t)
        fantas.UiKeyFrame(t, 'alpha', 255, 10, fantas.harmonic_curve).launch('continue')
    
    def clear_text(self):
        for i in self.text_temp:
            i.leave()
        self.text_temp.clear()
        self.size_kf.value = (self.size_kf.value[0], self.HEIGHT)
        self.size_kf.launch('continue')
        if not caculated_flag:
            self.title_text.text = "求解电路"
            self.title_text.update_img()
            self.title_text_color_kf.value = color.DARKBLUE
            self.title_text_color_kf.launch('continue')
            self.recover()

def show_data(component : Core.ElectricalComponent):
    global component_img
    branch = component.branch
    branch_data_text.text = f"所在支路：Node{branch.node_left.num} --- Node{branch.node_right.num}" 
    branch_data_text.update_img()
    if branch_data_text.is_root():
        branch_data_text.join_to(analysis.page, -1)

    v, p = Core.get_vp(branch.node_left.V)
    v, unit = Core.intelligent_output(v, Core.V_table, Core.V_k)
    # if v != 0:
    #     v = -v
    nodeleft_data_text.text = f"左节点：Node{branch.node_left.num}       {v:.2f}"
    nodeleft_data_text.update_img()
    nlda_text.rect.left = nodeleft_data_text.rect.right + 10
    nldp_text.text = f"{p:.2f}° {unit}"
    nldp_text.update_img()
    nldp_text.rect.left = nlda_text.rect.right + 10
    if nodeleft_data_text.is_root():
        nodeleft_data_text.join_to(analysis.page, -1)
    if nlda_text.is_root():
        nlda_text.join_to(analysis.page, -1)
    if nldp_text.is_root():
        nldp_text.join_to(analysis.page, -1)
        
    v, p = Core.get_vp(branch.node_right.V)
    v, unit = Core.intelligent_output(v, Core.V_table, Core.V_k)
    # if v != 0:
    #     v = -v
    noderight_data_text.text = f"右节点：Node{branch.node_right.num}       {v:.2f}"
    noderight_data_text.update_img()
    nrda_text.rect.left = noderight_data_text.rect.right + 10
    nrdp_text.text = f"{p:.2f}° {unit}"
    nrdp_text.update_img()
    nrdp_text.rect.left = nrda_text.rect.right + 10
    if noderight_data_text.is_root():
        noderight_data_text.join_to(analysis.page, -1)
    if nrda_text.is_root():
        nrda_text.join_to(analysis.page, -1)
    if nrdp_text.is_root():
        nrdp_text.join_to(analysis.page, -1)

    component_name_text.text = f"元件：{component.prefix}{component.num}"
    component_name_text.update_img()
    if component_name_text.is_root():
        component_name_text.join_to(analysis.page, -1)
    
    if component_img is not None:
        component_img.leave()
    component_img = COMPONENT_IMG[COMPONENT_CLASS.index(type(component))]
    component_img.join_to(analysis.page, -1)

    if component.Vref:
        posi_flag.rect.center = (topleft[0] + LEFT_FLAG_POS[0] + 10, topleft[1] + LEFT_FLAG_POS[1])
        nega_flag.rect.center = (topleft[0] + RIGHT_FLAG_POS[0] + 10, topleft[1] + RIGHT_FLAG_POS[1])
    else:
        posi_flag.rect.center = (topleft[0] + RIGHT_FLAG_POS[0] + 10, topleft[1] + RIGHT_FLAG_POS[1])
        nega_flag.rect.center = (topleft[0] + LEFT_FLAG_POS[0] + 10, topleft[1] + LEFT_FLAG_POS[1])
    if posi_flag.is_root():
        posi_flag.join_to(analysis.page, -1)
    if nega_flag.is_root():
        nega_flag.join_to(analysis.page, -1)
    
    if component.Iref:
        arrow.angle = 0
    else:
        arrow.angle = 180
    arrow.mark_update()
    if arrow.is_root():
        arrow.join_to(analysis.page, -1)
    
    v, p = Core.get_vp(component.U)
    v, unit = Core.intelligent_output(v, Core.V_table, Core.V_k)
    # if v != 0:
    #     v = -v
    U_data_text.text = f"电压：{v:.2f}"
    U_data_text.update_img()
    Ua_text.rect.left = U_data_text.rect.right + 10
    Up_text.text = f"{p:.2f}° {unit}"
    Up_text.update_img()
    Up_text.rect.left = Ua_text.rect.right + 10
    if U_data_text.is_root():
        U_data_text.join_to(analysis.page, -1)
    if Ua_text.is_root():
        Ua_text.join_to(analysis.page, -1)
    if Up_text.is_root():
        Up_text.join_to(analysis.page, -1)

    i, p = Core.get_vp(component.I)
    i, unit = Core.intelligent_output(i, Core.I_table, Core.I_k)
    # if component.Iref:
    #     i = -i
    I_data_text.text = f"电流：{i:.2f}"
    I_data_text.update_img()
    Ia_text.rect.left = I_data_text.rect.right + 10
    Ip_text.text = f"{p:.2f}° {unit}"
    Ip_text.update_img()
    Ip_text.rect.left = Ia_text.rect.right + 10
    if I_data_text.is_root():
        I_data_text.join_to(analysis.page, -1)
    if Ia_text.is_root():
        Ia_text.join_to(analysis.page, -1)
    if Ip_text.is_root():
        Ip_text.join_to(analysis.page, -1)

calculate_button = CalculateButton(midtop=(PAGEWIDTH / 2, LISTPADDING))
calculate_button.join(analysis.page)

branch_data_text = fantas.Text("所在支路：", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3_5, midleft=(LISTPADDING, calculate_button.rect.bottom + LISTPADDING + 48))
branch_data_text.anchor = 'midleft'

nodeleft_data_text = fantas.Text("左节点：", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3_5, midleft=(LISTPADDING, branch_data_text.rect.bottom + LISTPADDING))
nodeleft_data_text.anchor = 'midleft'
nlda_text = fantas.IconText(chr(0xe619), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3_5, midleft=(0, nodeleft_data_text.rect.centery))
nldp_text = fantas.Text("°", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3_5, midleft=(0, nodeleft_data_text.rect.centery))

noderight_data_text = fantas.Text("右节点：", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3_5, midleft=(LISTPADDING, nodeleft_data_text.rect.bottom + LISTPADDING))
noderight_data_text.anchor = 'midleft'
nrda_text = fantas.IconText(chr(0xe619), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3_5, midleft=(0, noderight_data_text.rect.centery))
nrdp_text = fantas.Text("°", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3_5, midleft=(0, noderight_data_text.rect.centery))

component_name_text = fantas.Text("元件：", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3_5, midleft=(LISTPADDING, noderight_data_text.rect.bottom + LISTPADDING + 48))
component_name_text.anchor = 'midleft'

topleft = (LISTPADDING, component_name_text.rect.bottom + LISTPADDING + 48)

if color.IS_DARKMODE:
    COMPONENT_IMG = (
        fantas.Ui(u.images['DARK_R'], topleft=topleft),
        fantas.Ui(u.images['DARK_C'], topleft=(topleft[0], topleft[1])),
        fantas.Ui(u.images['DARK_L'], topleft=(topleft[0], topleft[1])),
        fantas.Ui(u.images['DARK_Z'], topleft=(topleft[0], topleft[1])),
        fantas.Ui(u.images['DARK_U'], topleft=(topleft[0], topleft[1])),
        fantas.Ui(u.images['DARK_I'], topleft=(topleft[0], topleft[1])),
        fantas.Ui(u.images['DARK_kU'], topleft=(topleft[0], topleft[1])),
        fantas.Ui(u.images['DARK_kI'], topleft=(topleft[0], topleft[1])),
    )
else:
    COMPONENT_IMG = (
        fantas.Ui(u.images['R'], topleft=topleft),
        fantas.Ui(u.images['C'], topleft=(topleft[0], topleft[1])),
        fantas.Ui(u.images['L'], topleft=(topleft[0], topleft[1])),
        fantas.Ui(u.images['Z'], topleft=(topleft[0], topleft[1])),
        fantas.Ui(u.images['U'], topleft=(topleft[0], topleft[1])),
        fantas.Ui(u.images['I'], topleft=(topleft[0], topleft[1])),
        fantas.Ui(u.images['kU'], topleft=(topleft[0], topleft[1])),
        fantas.Ui(u.images['kI'], topleft=(topleft[0], topleft[1])),
    )
component_img = None

posi_flag = fantas.Text("+", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3_5)
nega_flag = fantas.Text("-", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3_5)
arrow = fantas.IconText(chr(0xe602), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_2, center=(topleft[0] + ARROW_POS[0] + 10, topleft[1] + ARROW_POS[1] + 10))

U_data_text = fantas.Text("电压：", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3_5, midleft=(LISTPADDING, topleft[1] + 128))
U_data_text.anchor = 'midleft'
Ua_text = fantas.IconText(chr(0xe619), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3_5, midleft=(0, U_data_text.rect.centery))
Up_text = fantas.Text("°", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3_5, midleft=(0, U_data_text.rect.centery))

I_data_text = fantas.Text("电流：", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3_5, midleft=(LISTPADDING, U_data_text.rect.bottom + LISTPADDING))
I_data_text.anchor = 'midleft'
Ia_text = fantas.IconText(chr(0xe619), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3_5, midleft=(0, I_data_text.rect.centery))
Ip_text = fantas.Text("°", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3_5, midleft=(0, I_data_text.rect.centery))
