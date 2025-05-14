import pygame
from pathlib import Path

import fantas
from fantas import uimanager as u

import Display.color as color
import Display.textstyle as textstyle
import Display.buttonstyle as buttonstyle

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

fantas.Text("三独立节点电路", u.fonts['shuhei'], textstyle.DARKBLUE_TITLE_3, midleft=(about_padding / 2, about_padding * 4)).join(about.page)
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
