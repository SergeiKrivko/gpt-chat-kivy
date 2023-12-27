from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDSeparator
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar

from src.gpt.chat import GPTChat


class ChatSettingsScreen(MDScreen):
    def __init__(self, app: MDApp):
        super().__init__(name='ChatSettings')
        self.app = app

        main_layout = MDBoxLayout(orientation='vertical')
        self.add_widget(main_layout)

        self.top_bar = MDTopAppBar(title='Chat settings')
        self.top_bar.left_action_items = [['arrow-left', lambda x: self.on_closed()]]
        main_layout.add_widget(self.top_bar)

        layout = MDBoxLayout(orientation='vertical', adaptive_height=True)
        layout.padding = 40
        layout.spacing = 15
        main_layout.add_widget(layout)

        layout.add_widget(MDLabel(text="Chat name:", adaptive_height=True))
        self.chat_name_edit = MDTextField(mode='round')
        layout.add_widget(self.chat_name_edit)

        main_layout.add_widget(MDBoxLayout())

        self._chat: GPTChat | None = None

    def open_chat(self, chat: GPTChat):
        self._chat = chat

        self.chat_name_edit.text = chat.name if chat.name else ''

    def save_chat(self):
        if self._chat is None:
            return
        self._chat.name = self.chat_name_edit.text
