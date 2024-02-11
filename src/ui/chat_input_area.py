from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.textfield import MDTextField


class ChatInputArea(MDTextField):
    def __init__(self, app: MDApp):
        super().__init__()
        self.app = app
        self.theme_line_height = 'Custom'

        self.multiline = True
        self.mode = "outlined"
        self.size_hint_y = None
        self.radius = dp(15)

    def set_theme(self):
        pass
        # self.line_color_normal = self.app.theme_cls.primaryContainerColor
