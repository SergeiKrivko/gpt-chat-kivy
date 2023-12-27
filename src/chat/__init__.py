import os
import platform
import sys

from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from src.chat.chat_list import ChatsList, ChatListWidgetItem
from src.chat.chat_widget import ChatWidget
from src.gpt.chat import GPTChat
# from src.gpt.database import Database
from src.ui.main_settings_screen import MainSettingsScreen


class ChatPanel(BoxLayout):
    def __init__(self, app: MDApp):
        super().__init__(orientation="vertical")
        self.app = app

        if platform.system() == 'Windows':
            app_data_dir = os.path.dirname(sys.argv[0])
        else:
            app_data_dir = app.user_data_dir

        # self.db = Database(app_data_dir)

        self._screen_manager = MDScreenManager()
        self.add_widget(self._screen_manager)

        self.chat_list = ChatsList(self.app)
        self.chat_list.top_panel.on_settings_clicked = self.open_settings
        self.chat_list.on_chat_deleted = self.delete_chat
        self._screen_manager.add_widget(self.chat_list)
        self.chat_list.top_panel.on_chat_added = self.new_chat

        self.settings_screen = MainSettingsScreen(self.app)
        self.settings_screen.on_closed = self.close_settings
        self._screen_manager.add_widget(self.settings_screen)

        self.chat_widgets = dict()
        self.current_chat: int | None = None

        # for chat in self.db.chats:
        #     self.add_chat(chat)

    def add_chat(self, chat: GPTChat):
        widget = ChatWidget(self.app, chat)
        widget.top_panel.on_chat_closed = self.hide_chat
        self._screen_manager.add_widget(widget)
        item = self.chat_list.add_item(chat)
        item.on_clicked = self._on_list_widget_item_clicked
        self.chat_widgets[chat.id] = widget

    def delete_chat(self, chat):
        self._screen_manager.remove_widget(self.chat_widgets[chat.id])
        self.chat_widgets.pop(chat.id)

    def _on_list_widget_item_clicked(self, item: ChatListWidgetItem):
        self.show_chat(item.chat)

    def new_chat(self):
        chat = self.db.add_chat()
        self.add_chat(chat)

    def show_chat(self, chat: GPTChat):
        self._screen_manager.transition.direction = 'left'
        self._screen_manager.current = f'Chat{chat.id}'
        self.chat_widgets[chat.id].load_messages()
        self.current_chat = chat.id

    def hide_chat(self):
        if self.current_chat is None:
            return
        self._screen_manager.transition.direction = 'right'
        self._screen_manager.current = 'Chats'
        self.current_chat = None

    def open_settings(self):
        self._screen_manager.transition.direction = 'left'
        self._screen_manager.current = 'Settings'

    def close_settings(self):
        self._screen_manager.transition.direction = 'right'
        self._screen_manager.current = 'Chats'

