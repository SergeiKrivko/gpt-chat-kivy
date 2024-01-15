from typing import Union

from kivy.metrics import dp
from kivymd.uix.slider import MDSlider
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDSeparator
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar

import g4f
from src.gpt.chat import GPTChat
from src.ui.select_area import SelectionItem


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
        layout.padding = dp(20)
        layout.spacing = dp(15)
        main_layout.add_widget(layout)

        layout.add_widget(MDLabel(text="Chat name:", adaptive_height=True))
        self.chat_name_edit = MDTextField(mode='round')
        layout.add_widget(self.chat_name_edit)

        layout.add_widget(MDSeparator())

        self.model_edit = SelectionItem(self, "Model", ['default'] + g4f.models.Model.__all__())
        layout.add_widget(self.model_edit)

        layout.add_widget(MDSeparator())

        layout.add_widget(MDLabel(text="Used messages:", adaptive_height=True))
        self.used_messages_edit = MDSlider(min=1, max=10, size_hint_y=None, height=dp(30))
        layout.add_widget(self.used_messages_edit)

        layout.add_widget(MDSeparator())

        layout.add_widget(MDLabel(text="Saved messages:", adaptive_height=True))
        self.saved_messages_edit = MDSlider(min=50, max=1000, size_hint_y=None, height=dp(30))
        layout.add_widget(self.saved_messages_edit)

        layout.add_widget(MDSeparator())

        layout.add_widget(MDLabel(text="Temperature:", adaptive_height=True))
        self.temperature_edit = MDSlider(min=0, max=100, size_hint_y=None, height=dp(30))
        layout.add_widget(self.temperature_edit)

        main_layout.add_widget(MDBoxLayout())

        self._chat: Union[GPTChat, None] = None

    def open_chat(self, chat: GPTChat):
        self._chat = chat

        self.chat_name_edit.text = chat.name if chat.name else ''
        self.model_edit.current = 'default' if not chat.model else chat.model
        self.used_messages_edit.value = chat.used_messages
        self.saved_messages_edit.value = chat.saved_messages
        self.temperature_edit.value = int(chat.temperature * 100)

    def save_chat(self):
        if self._chat is None:
            return
        self._chat.name = self.chat_name_edit.text
        self._chat.model = self.model_edit.current
        self._chat.used_messages = self.used_messages_edit.value
        self._chat.saved_messages = self.saved_messages_edit.value
        self._chat.temperature = self.temperature_edit.value / 100
        self._chat._db.commit()
