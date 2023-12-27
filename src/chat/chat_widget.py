from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar

# from src.gpt import stream_response
from src.gpt.chat import GPTChat


class ChatWidget(MDScreen):
    def __init__(self, app: MDApp, chat: GPTChat):
        super().__init__(name=f'Chat{chat.id}')
        self.chat = chat
        self.app = app

        main_layout = BoxLayout(orientation='vertical')
        self.add_widget(main_layout)

        self.top_panel = ChatTopPanel(self.chat)
        main_layout.add_widget(self.top_panel)


class ChatTopPanel(MDTopAppBar):
    def __init__(self, chat: GPTChat):
        super().__init__()
        self.title = chat.name if chat.name else 'Chat'
        self.left_action_items = [['arrow-left', self.close_chat]]
        self.right_action_items = [['dots-horizontal', lambda x: x]]

        self.on_chat_closed = None

    def close_chat(self, *args):
        if self.on_chat_closed is not None:
            self.on_chat_closed()
