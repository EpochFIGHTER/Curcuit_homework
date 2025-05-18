import pygame
# from pathlib import Path

import fantas
from fantas import uimanager as u

import Display.color as color
import Display.textstyle as textstyle
import Display.buttonstyle as buttonstyle
import Display.viewbox as viewbox

from Core.Component import nodes, ElectricalBranch

SIDEBAR_LEFT = u.WIDTH / 4 * 3


class SidebarPageMouseWidget(fantas.MouseBase):
    def __init__(self, page):
        super().__init__(page, 2)\
    
    def mousein(self):
        if not self.ui.poped and not self.ui.pre_poped:
            self.ui.pre_pop()

    def mouseout(self):
        if not self.ui.poped and self.ui.pre_poped:
            self.ui.back()
    
    def mouseclick(self):
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
fantas.Text("正弦稳态电路分析器 V1.0", u.fonts['shuhei'], textstyle.DARKBLUE_TITLE_3, midleft=(about_padding / 2, about_padding * 4 + about_lineheight)).join(about.page)
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
fantas.Text("Python 3.12.7", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, midright=(about_padding * 7 / 2, about_padding * 4 + about_lineheight * 11)).join(about.page)
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

    def append(self, node):
        super().append(node)
        self.set_size((PAGEWIDTH, self.rect.h + node.MAX_HEIGHT + LISTPADDING))

    def remove(self, node):
        super().remove(node)
        self.set_size((PAGEWIDTH, self.rect.h - node.MAX_HEIGHT - LISTPADDING))

    def insert(self, node, index):
        super().insert(node, index)
        self.set_size((PAGEWIDTH, self.rect.h + node.MAX_HEIGHT + LISTPADDING))
        if index < 0:
            index = len(self.kidgroup) + index
        self.move(index, node.size_kf.value[1] + LISTPADDING)

    def move(self, index, distance):
        for k in self.kidgroup[index:]:
            k.top_kf.value += distance
            k.top_kf.launch('continue')

    def add_height(self, height):
        self.set_size((PAGEWIDTH, self.rect.h + height))

branch_list = BranchList()
branch_list.join(structure.page)

class ComponentList(fantas.Label):
    def __init__(self, **anchor):
        super().__init__((PAGEWIDTH - LISTPADDING * 2, 0), **anchor)
        self.anchor = 'topleft'
        self.top_kf = fantas.RectKeyFrame(self, 'top', 0, 10, fantas.slower_curve)
        self.mousewidget = BranchListMouseWidget(self)
        self.mousewidget.apply_event()

    def append(self, node):
        super().append(node)
        self.set_size((PAGEWIDTH, self.rect.h + node.MAX_HEIGHT + LISTPADDING))

    def remove(self, node):
        super().remove(node)
        self.set_size((PAGEWIDTH, self.rect.h - node.MAX_HEIGHT - LISTPADDING))
    
    def insert(self, node, index):
        super().insert(node, index)
        self.set_size((PAGEWIDTH, self.rect.h + node.MAX_HEIGHT + LISTPADDING))
        if index < 0:
            index = len(self.kidgroup) + index
        self.move(index, node.size_kf.value[1] + LISTPADDING)
    
    def move(self, index, distance):
        for k in self.kidgroup[index:]:
            k.top_kf.value += distance
            k.top_kf.launch('continue')

    def add_height(self, height):
        self.set_size((PAGEWIDTH, self.rect.h + height))

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
                l = fantas.Label((self.ui.rect.w / 4 - 16, 4), bg=color.DARKBLUE, center=(self.ui.rect.w / 4 * (pressed_node + 1), self.ui.HEIGHT * 3 / 2))
                l.join(self.ui)
                self.line.append(l)
            elif d > 1:
                l = fantas.Label((4, 16), bg=color.DARKBLUE, radius={'border_bottom_left_radius': 2, 'border_bottom_right_radius': 2}, midtop=(self.ui.rect.w / 8 * (pressed_node * 2 + 1), self.ui.HEIGHT * 3 / 2 + 8))
                l.join(self.ui)
                self.line.append(l)
                l = fantas.Label((4, 16), bg=color.DARKBLUE, radius={'border_bottom_left_radius': 2, 'border_bottom_right_radius': 2}, midtop=(self.ui.rect.w / 8 * (released_node * 2 + 1), self.ui.HEIGHT * 3 / 2 + 8))
                l.join(self.ui)
                self.line.append(l)
                l = fantas.Label((self.ui.rect.w / 4 * d, 4), bg=color.DARKBLUE, radius={'border_bottom_left_radius': 2, 'border_bottom_right_radius': 2}, midleft=(self.ui.rect.w / 8 * (pressed_node * 2 + 1), self.ui.HEIGHT * 3 / 2 + 24))
                l.join(self.ui)
                self.line.append(l)

    def mousepress(self, pos, button):
        if button == pygame.BUTTON_LEFT and self.ui.status == 1:
            if not self.mouseon:
                self.ui.hide_choose_branch()
            elif self.ui.HEIGHT < pos[1] - self.ui.rect.top < self.ui.HEIGHT * 2:
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
    HEIGHT = 80
    MAX_HEIGHT = HEIGHT * 2
    BG = color.LIGHTGREEN

    def __init__(self, **anchor):
        super().__init__((PAGEWIDTH - LISTPADDING * 2, self.HEIGHT), buttonstyle.branch_list_button_style, 2, radius={'border_radius': 16}, **anchor)
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

        self.size_kf = fantas.LabelKeyFrame(self, 'size', (PAGEWIDTH - LISTPADDING * 2, self.HEIGHT), 10, fantas.harmonic_curve)
        self.top_kf = fantas.RectKeyFrame(self, 'top', self.rect.top, 10, fantas.harmonic_curve)

    def add_choose_node(self, node1, node2):
        BranchUi(node1, node2)
        self.hide_choose_branch()

    def show_choose_branch(self):
        self.ban()
        self.status = 1
        self.banned_mousewidget.mouseon = True
        self.size_kf.value = (PAGEWIDTH - LISTPADDING * 2, self.HEIGHT * 2)
        self.size_kf.launch('continue')
        self.add_icon.leave()
        self.add_text.join(self)
        for i in self.choose_nodes:
            i.join(self)

    def hide_choose_branch(self):
        self.status = 0
        self.recover()
        self.size_kf.value = (PAGEWIDTH - LISTPADDING * 2, self.HEIGHT)
        self.size_kf.launch('continue')
        self.add_icon.join(self)
        self.add_text.leave()
        for i in self.choose_nodes:
            i.leave()

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

        self.unfold_button = fantas.SmoothColorButton((self.INIT_HEIGHT - self.PADDING * 2, self.INIT_HEIGHT - self.PADDING * 2), buttonstyle.common_button_style, 2, radius={'border_radius': 16}, topleft=(self.PADDING, self.PADDING))
        self.unfold_button.join(self)
        self.unfold_button.bind(self.unfold)
        self.unfold_icon = fantas.IconText(chr(0xe60e), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3, center=(self.unfold_button.rect.w / 2, self.unfold_button.rect.h / 2))
        self.unfold_icon.angle = 90
        self.unfold_icon.join(self.unfold_button)
        self.unfold_icon_angle_kf = fantas.UiKeyFrame(self.unfold_icon, 'angle',90, 10, fantas.harmonic_curve)

        self.title_text = fantas.Text(f"n{node1.num} --- n{node2.num}", u.fonts['deyi'], textstyle.DARKBLUE_TITLE_3, center=(self.rect.w / 2, self.unfold_button.rect.centery))
        self.title_text.join(self)

        self.delete_button = fantas.SmoothColorButton((self.INIT_HEIGHT - self.PADDING * 2, self.INIT_HEIGHT - self.PADDING * 2), buttonstyle.warn_button_style, 2, radius={'border_radius': 16}, topright=(self.rect.w - self.PADDING, self.PADDING))
        self.delete_button.join(self)
        self.delete_button.bind(self.delete)
        self.delete_icon = fantas.IconText(chr(0xe66b), u.fonts['iconfont'], textstyle.DARKBLUE_TITLE_3, center=(self.delete_button.rect.w / 2, self.delete_button.rect.h / 2))
        self.delete_icon.join(self.delete_button)

        self.component_list = ComponentList(midtop=(self.rect.w / 2, self.INIT_HEIGHT))
        self.component_list.join(self)
        self.add_component_button = AddComponentButton(midtop=(self.rect.w / 2, self.PADDING)).join(self.component_list)

    def unfold(self):
        self.size_kf.value = (PAGEWIDTH - LISTPADDING * 2, self.INIT_HEIGHT + self.component_list.rect.h + self.PADDING * 2)
        self.size_kf.launch('continue')
        branch_list.add_height(self.component_list.rect.h + self.PADDING * 2)
        branch_list.move(self.get_index() + 1, self.component_list.rect.h + self.PADDING * 2)
        self.unfold_button.bind(self.fold)
        self.unfold_icon_angle_kf.value = 0
        self.unfold_icon_angle_kf.launch('continue')
    
    def fold(self):
        self.size_kf.value = (PAGEWIDTH - LISTPADDING * 2, self.INIT_HEIGHT)
        self.size_kf.launch('continue')
        branch_list.add_height(-self.component_list.rect.h - self.PADDING * 2)
        branch_list.move(self.get_index() + 1, -self.component_list.rect.h - self.PADDING * 2)
        self.unfold_button.bind(self.unfold)
        self.unfold_icon_angle_kf.value = 90
        self.unfold_icon_angle_kf.launch('continue')

    def delete(self):
        pass

class AddComponentMouseWidget(fantas.MouseBase):
    def __init__(self, ui):
        super().__init__(ui, 2)
    
    def mousepress(self, pos, button):
        if button == pygame.BUTTON_LEFT and self.ui.status == 1:
            if not self.mouseon:
                self.ui.hide_choose_component()        

class AddComponentButton(fantas.SmoothColorButton):
    HEIGHT = 80
    MAX_HEIGHT = HEIGHT * 2
    BG = color.LIGHTGREEN

    def __init__(self, **anchor):
        super().__init__((PAGEWIDTH - LISTPADDING * 4, self.HEIGHT), buttonstyle.branch_list_button_style, 2, radius={'border_radius': 16}, **anchor)
        self.anchor = 'midtop'
        self.bind(self.show_choose_component)
        self.banned_mousewidget = AddComponentMouseWidget(self)
        self.status = 0
    
        self.add_icon = fantas.IconText(chr(0xe620), u.fonts['iconfont'], textstyle.GRAY_TITLE_3, center=(self.rect.w / 2, self.rect.h / 2))
        self.add_icon.join(self)
        self.add_text = fantas.Text("选择元件类型", u.fonts['deyi'], textstyle.GRAY_TITLE_3, center=(self.rect.w / 2, self.rect.h / 2))

        self.choose_components = []
        for i in range(8):
            self.choose_components.append(ChooseComponentButton(i, center=(self.rect.w / 16 * (i * 2 + 1), self.rect.h / 2 * 3)))

        self.size_kf = fantas.LabelKeyFrame(self, 'size', (PAGEWIDTH - LISTPADDING * 4, self.HEIGHT), 10, fantas.harmonic_curve)
        self.top_kf = fantas.RectKeyFrame(self, 'top', self.rect.top, 10, fantas.harmonic_curve)
    
    def show_choose_component(self):
        self.ban()
        self.status = 1
        self.banned_mousewidget.mouseon = True
        self.size_kf.value = (PAGEWIDTH - LISTPADDING * 4, self.HEIGHT * 2)
        self.size_kf.launch('continue')
        self.add_icon.leave()
        self.add_text.join(self)
        for i in self.choose_components:
            i.join(self)
    
    def hide_choose_component(self):
        self.status = 0
        self.recover()
        self.size_kf.value = (PAGEWIDTH - LISTPADDING * 4, self.HEIGHT)
        self.size_kf.launch('continue')
        self.add_icon.join(self)
        self.add_text.leave()
        for i in self.choose_components:
            i.leave()

    def ban(self):
        super().ban()
        self.banned_mousewidget.apply_event()

    def recover(self):
        super().recover()
        self.banned_mousewidget.cancel_event()

class ChooseComponentButtonMouseWidget(fantas.ColorButtonMouseWidget):
    pass

class ChooseComponentButton(fantas.SmoothColorButton):
    IMG_NAME = ('R', 'C', 'L', 'Z', 'U', 'I', 'kU', 'kI')
    COMPONENT_NAME = ('电阻', '电容', '电感', '阻抗', '独立电压源', '独立电流源', '受控电压源', '受控电流源')
    SIZE = 40

    def __init__(self, num, **kwargs):
        super().__init__((self.SIZE, self.SIZE), buttonstyle.common_button_style, 2, ChooseComponentButtonMouseWidget, **kwargs)
        self.icon = fantas.Ui(u.images[self.IMG_NAME[num]], center=(self.rect.w / 2, self.rect.h / 2))
        self.icon.size = (self.SIZE, self.SIZE * 80 / 180)
        self.icon.join(self)
        self.apply_size()

