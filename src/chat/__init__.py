import os
import platform
import sys
from typing import Union

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screenmanager import MDScreenManager

from src.auth import AuthManager
from src.chat.chat_list import ChatsList, ChatListWidgetItem
from src.chat.chat_widget import ChatWidget
from src.database import ChatManager
from src.gpt.chat import GPTChat
from src.settings_manager import SettingsManager
from src.ui.chat_settings_screen import ChatSettingsScreen
from src.ui.main_settings_screen import MainSettingsScreen


class ChatPanel(MDBoxLayout):
    def __init__(self, app: MDApp):
        super().__init__(orientation="vertical")
        self.app = app

        if platform.system() == 'Windows':
            app_data_dir = os.path.dirname(sys.argv[0])
        else:
            app_data_dir = app.user_data_dir
        self.app_data_dir = app_data_dir
        os.makedirs(f"{self.app_data_dir}/temp", exist_ok=True)

        import g4f.Provider.helper
        g4f.Provider.helper.user_data_dir = os.path.join(app_data_dir, 'g4f')

        self.sm = SettingsManager(app_data_dir)
        self._chat_manager = ChatManager(self.sm)
        self.app.theme_cls.theme_style = 'Dark' if self.sm.get('dark', True) else 'Light'
        self.app.theme_cls.primary_palette = self.sm.get('theme', 'Blue')

        self._screen_manager = MDScreenManager()
        self.add_widget(self._screen_manager)

        self.chat_list = ChatsList(self.app)
        self.chat_list.top_panel.on_settings_clicked = self.open_settings
        self.chat_list.on_chat_deleted = self._chat_manager.delete_chat
        self._screen_manager.add_widget(self.chat_list)
        self.chat_list.top_panel.on_chat_added = self.new_chat

        self.settings_screen = MainSettingsScreen(self.app, self.sm)
        self.settings_screen.on_closed = self.close_settings
        self._screen_manager.add_widget(self.settings_screen)

        self._sign_in_manager = AuthManager(self.app, self.sm, self._screen_manager)
        self._sign_in_manager.on_auth = self.close_auth

        self.chat_settings_screen = ChatSettingsScreen(self.app, self._chat_manager)
        self.chat_settings_screen.on_closed = self.close_chat_settings
        self._screen_manager.add_widget(self.chat_settings_screen)

        self.chat_widgets = dict()
        self.current_chat: Union[GPTChat, None] = None

        self._chat_manager.on_new_chat = self.add_chat
        self._chat_manager.on_update_chat = lambda *args: None
        self._chat_manager.on_delete_chat = self.on_chat_deleted
        self._chat_manager.on_delete_remote_chat = self._on_remote_chat_deleted
        self._chat_manager.on_new_message = self._on_new_message
        self._chat_manager.on_delete_message = self._on_delete_message
        if self.sm.get('user_id'):
            self._chat_manager.auth()

    def add_chat(self, chat: GPTChat):
        widget = ChatWidget(self.app, self.sm, self._chat_manager, chat)
        widget.top_panel.on_chat_closed = self.hide_chat
        widget.top_panel.on_settings_clicked = self.open_chat_settings
        self._screen_manager.add_widget(widget)
        item = self.chat_list.add_item(chat)
        item.on_clicked = self._on_list_widget_item_clicked
        self.chat_widgets[chat.id] = widget

    def on_chat_deleted(self, chat_id):
        self._screen_manager.remove_widget(self.chat_widgets[chat_id])
        self.chat_list.remove_chat(chat_id)
        self.chat_widgets.pop(chat_id)

    def _on_list_widget_item_clicked(self, item: ChatListWidgetItem):
        self.show_chat(item.chat)

    def new_chat(self):
        self._chat_manager.new_chat()

    def _on_new_message(self, chat_id, message):
        widget = self.chat_widgets[chat_id]
        widget.add_bubble(message)

    def _on_delete_message(self, chat_id, message):
        widget = self.chat_widgets[chat_id]
        widget.delete_bubble(message)

    def show_chat(self, chat: GPTChat):
        self._screen_manager.transition.direction = 'left'
        self._screen_manager.current = f'Chat{chat.id}'
        self.chat_widgets[chat.id].load_messages()
        self.current_chat = chat

    def hide_chat(self):
        if self.current_chat is None:
            return
        self._screen_manager.transition.direction = 'right'
        self._screen_manager.current = 'Chats'
        self.chat_list.update_name(self.current_chat)
        self.current_chat = None

    def open_settings(self):
        self._screen_manager.transition.direction = 'left'
        self._screen_manager.current = 'Settings'

    def close_settings(self):
        self._screen_manager.transition.direction = 'right'
        self._screen_manager.current = 'Chats'

    def open_chat_settings(self):
        self._screen_manager.transition.direction = 'left'
        self._screen_manager.current = 'ChatSettings'
        self.chat_settings_screen.open_chat(self.current_chat)

    def close_chat_settings(self):
        self._screen_manager.transition.direction = 'right'
        self._screen_manager.current = f'Chat{self.current_chat.id}'
        self.chat_settings_screen.save_chat()

    def close_auth(self):
        self._screen_manager.current = 'Chats'
        self._chat_manager.auth()

    def on_close(self):
        self._chat_manager.close()

    def _on_remote_chat_deleted(self, chat):
        RemoteDeletedDialog(self._chat_manager, chat).open()


class RemoteDeletedDialog(MDDialog):
    def __init__(self, chat_manager: ChatManager, chat):
        self._chat_manager = chat_manager
        self._chat = chat
        super().__init__(
            text=f"The synchronization of the chat {chat.name} has been stopped. Delete a local copy of the chat?",
            buttons=[
                MDFlatButton(
                    text="No",
                    # theme_text_color="Custom",
                    # text_color=self.theme_cls.primary_color,
                    on_release=self._on_no,
                ),
                MDFlatButton(
                    text="Yes",
                    # theme_text_color="Custom",
                    # text_color=self.theme_cls.primary_color,
                    on_release=self._on_yes,
                ),
            ])

    def _on_yes(self, *args):
        self._chat_manager.delete_chat(self._chat.id)
        self.dismiss()

    def _on_no(self, *args):
        self._chat.remote_id = None
        self.dismiss()
