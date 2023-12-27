from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar


class ChatsList(MDScreen):
    def __init__(self, app):
        super().__init__(name='Chats')
        self.app = app

        main_layout = BoxLayout(orientation='vertical')
        self.add_widget(main_layout)

        self.top_panel = ListTopPanel()
        main_layout.add_widget(self.top_panel)


class ListTopPanel(MDTopAppBar):
    def __init__(self):
        super().__init__()
        self.title = "Chats"
        self.left_action_items = [['plus', lambda x: x]]
        self.right_action_items = [['dots-horizontal', lambda x: self.on_settings_clicked()]]
