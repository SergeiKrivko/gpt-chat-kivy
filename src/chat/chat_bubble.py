from kivymd.app import MDApp
from kivymd.material_resources import dp
from kivymd.uix.behaviors import StencilBehavior
from kivymd.uix.label import MDLabel

from src.gpt.message import GPTMessage


class ChatBubble(MDLabel, StencilBehavior):
    def __init__(self, app: MDApp, message: GPTMessage):
        text = message.content
        side = 'right' if message.role == 'user' else 'left'
        super().__init__()
        self.message = message
        self.app = app
        self.allow_selection = True
        self.adaptive_height = True
        self.padding = dp(10)
        self.size_hint_x = 0.8
        self.text = text
        if side == 'right':
            self.md_bg_color = self.app.theme_cls.primary_dark if self.app.theme_cls.theme_style == 'Dark' else \
                self.app.theme_cls.primary_light
        else:
            self.md_bg_color = self.app.theme_cls.bg_light if self.app.theme_cls.theme_style == 'Dark' else \
                self.app.theme_cls.bg_darkest
        self.radius = (dp(10), dp(10), 0 if side == 'right' else dp(10), 0 if side == 'left' else dp(10))
        self.pos_hint = {'center_x': 0.4 if side == 'left' else 0.6}

    def add_text(self, text):
        self.text += text
        self.message.add_text(text)
