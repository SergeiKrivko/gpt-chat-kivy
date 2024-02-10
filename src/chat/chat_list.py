from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivymd.uix.card import MDCardSwipe, MDCardSwipeLayerBox, MDCardSwipeFrontBox
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar, MDBottomAppBar

from src.gpt.chat import GPTChat


class ChatsList(MDScreen):
    def __init__(self, app):
        super().__init__(name='Chats')
        self.app = app

        main_layout = MDBoxLayout(orientation='vertical')
        self.add_widget(main_layout)

        self.top_panel = ListTopPanel()
        main_layout.add_widget(self.top_panel)

        self.scroll_view = MDScrollView()
        self.scroll_view.scroll_timeout = 100
        main_layout.add_widget(self.scroll_view)
        self.list = MDList()
        self.scroll_view.add_widget(self.list)

        # main_layout.add_widget(MDTopAppBar())

        self.on_chat_deleted = None
        self._items = dict()

    def add_item(self, chat: GPTChat) -> 'ChatListWidgetItem':
        item = ChatListWidgetItem(self.app, chat)
        item.on_deleted = self.remove_item
        self.list.add_widget(item)
        self._items[chat.id] = item
        return item

    def remove_item(self, item: 'ChatListWidgetItem'):
        self.list.remove_widget(item)
        if self.on_chat_deleted:
            self.on_chat_deleted(item.chat.id)
        self._items.pop(item.chat.id)

    def update_name(self, chat):
        self._items[chat.id].update_name()


class ChatListWidgetItem(MDCardSwipe):
    def __init__(self, app: MDApp, chat: GPTChat):
        super().__init__()
        self.app = app
        self.size_hint_y: None
        self.adaptive_height = True
        self.radius = 0

        self.back_box = MDCardSwipeLayerBox()
        self.add_widget(self.back_box)
        self.back_box.bg_color = self.app.theme_cls.bg_normal

        self.front_box = MDCardSwipeFrontBox()
        self.front_box.radius = 0
        self.add_widget(self.front_box)
        self.type_swipe = 'auto'

        self.chat = chat

        self.list_item = OneLineListItem()
        self.update_name()
        self.list_item._no_ripple_effect = True
        self.list_item.bind(on_press=lambda *args: self._set_pressed(True), on_release=self._on_released)
        self.bind(on_touch_move=lambda *args: self._set_pressed(False))
        self.front_box.add_widget(self.list_item)

        self.height = self.list_item.height

        self.on_deleted = None
        self.on_clicked = None
        self._pressed = False

    def update_name(self):
        name = self.chat.name
        if not name:
            if self.chat.last_message is None:
                name = "<Новый диалог>"
            else:
                name = self.chat.last_message.content
        self.list_item.text = name

    def _set_pressed(self, flag):
        self._pressed = flag

    def _on_released(self, arg):
        if self._pressed and self.on_clicked:
            self.on_clicked(self)

    def _on_swipe_complete(self, *args):
        super()._on_swipe_complete(*args)
        if self.on_deleted is not None:
            self.on_deleted(self)


class ListTopPanel(MDTopAppBar):
    def __init__(self):
        super().__init__()
        self.title = "Chats"
        self.left_action_items = [['plus', lambda x: None if self.on_chat_added is None else self.on_chat_added()]]
        self.right_action_items = [['dots-horizontal', lambda x: self.on_settings_clicked()]]
