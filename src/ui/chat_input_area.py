from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.textfield import MDTextField


class ChatInputArea(MDTextField):
    def __init__(self, app: MDApp):
        super().__init__()
        self.app = app

        self.multiline = True
        self.hint_text = 'Сообщение'
        self.mode = "fill"
        self.size_hint_y = None
        self.radius = [dp(0), dp(0), dp(0), dp(0)]

        self.text_color_normal = app.theme_cls.bg_normal
        self.text_color_focus = app.theme_cls.bg_normal
        self.hint_text_color_normal = app.theme_cls.bg_normal
        self.hint_text_color_focus = app.theme_cls.primary_color
        self.line_color_normal = app.theme_cls.primary_color
        self.line_color_focus = app.theme_cls.primary_color
        self.fill_color_normal = app.theme_cls.primary_color
        self.fill_color_focus = app.theme_cls.primary_color
        self.line_height = 0

        # self.multiline = True
        # # self.hint_text = 'Сообщение'
        # self.mode = "rectangle"
        # self.size_hint_y = None
        # self.radius = [dp(25), dp(25), dp(25), dp(25)]
        #
        # self.text_color_normal = self.app.theme_cls.bg_normal
        # self.text_color_focus = self.app.theme_cls.bg_normal
        # self.hint_text_color_normal = self.app.theme_cls.bg_normal
        # self.hint_text_color_focus = self.app.theme_cls.bg_normal
        # self.line_color_normal = self.app.theme_cls.bg_normal
        # self.line_color_focus = self.app.theme_cls.bg_normal
