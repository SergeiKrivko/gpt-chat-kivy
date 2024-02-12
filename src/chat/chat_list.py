from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonIcon
from kivymd.uix.card import MDCardSwipe, MDCardSwipeLayerBox, MDCardSwipeFrontBox
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.appbar import MDTopAppBar, MDTopAppBarTitle, MDTopAppBarTrailingButtonContainer, \
    MDActionTopAppBarButton, MDTopAppBarLeadingButtonContainer

from src.gpt.chat import GPTChat


class ChatsList(MDScreen):
    def __init__(self, app):
        super().__init__(name='Chats')
        self.app = app
        self.theme_bg_color = 'Custom'

        main_layout = MDBoxLayout(orientation='vertical')
        self.add_widget(main_layout)

        self.top_panel = ListTopPanel()
        main_layout.add_widget(self.top_panel)

        self.scroll_view = MDScrollView()
        self.scroll_view.scroll_timeout = 100
        main_layout.add_widget(self.scroll_view)
        self.list = MDList()
        self.scroll_view.add_widget(self.list)

        self.on_chat_deleted = None
        self._items = dict()

    def add_item(self, chat: GPTChat) -> 'ChatListWidgetItem':
        item = ChatListWidgetItem(self.app, chat)
        item.on_deleted = self.remove_item
        self.list.add_widget(item)
        self._items[chat.id] = item
        return item

    def remove_chat(self, chat_id):
        for item in self._items.values():
            if item.chat.id == chat_id:
                self.list.remove_widget(item)
                self._items.pop(item.chat.id)
                break

    def remove_item(self, item: 'ChatListWidgetItem'):
        self.list.remove_widget(item)
        if self.on_chat_deleted:
            self.on_chat_deleted(item.chat.id)
        self._items.pop(item.chat.id)

    def update_name(self, chat):
        self._items[chat.id].update_name()

    def set_theme(self):
        self.md_bg_color = self.theme_cls.backgroundColor
        self.top_panel.md_bg_color = self.theme_cls.primaryContainerColor
        for item in self._items.values():
            item.set_theme()


class ChatListWidgetItem(MDCardSwipe):
    def __init__(self, app: MDApp, chat: GPTChat):
        super().__init__()
        self.app = app
        self.size_hint_y: None
        self.adaptive_height = True
        self.radius = 0
        self.theme_bg_color = 'Custom'

        # self.back_box = MDCardSwipeLayerBox(MDButton(MDButtonIcon(icon='trash-can'), center_y=0.5, ripple_effect=False),
        #                                     theme_bg_color='Custom', padding=dp(8))
        self.back_box = MDCardSwipeLayerBox(theme_bg_color='Custom')
        self.add_widget(self.back_box)

        self.front_box = MDCardSwipeFrontBox()
        self.front_box.radius = 0
        self.add_widget(self.front_box)
        self.type_swipe = 'auto'

        self.chat = chat

        self.list_item = MDListItem(item_text := MDListItemHeadlineText(),
                                    on_press=lambda *args: self._set_pressed(True), on_release=self._on_released,
                                    ripple_effect=False, theme_bg_color='Custom')
        self.list_item_text = item_text

        self.update_name()
        self.bind(on_touch_move=lambda *args: self._set_pressed(False))
        self.front_box.add_widget(self.list_item)

        self.height = self.list_item.height

        self.on_deleted = None
        self.on_clicked = None
        self._pressed = False
        self.set_theme()

    def update_name(self):
        name = self.chat.name
        if not name:
            if self.chat.last_message is None:
                name = "<Новый диалог>"
            else:
                name = self.chat.last_message.content
        self.list_item_text.text = name

    def _set_pressed(self, flag):
        self._pressed = flag

    def _on_released(self, arg):
        if self._pressed and self.on_clicked:
            self.on_clicked(self)

    def _on_swipe_complete(self, *args):
        super()._on_swipe_complete(*args)
        if self.on_deleted is not None:
            self.on_deleted(self)

    def set_theme(self):
        self.back_box.md_bg_color = self.app.theme_cls.surfaceColor
        self.list_item.md_bg_color = self.app.theme_cls.secondaryContainerColor
        self.front_box.md_bg_color = self.app.theme_cls.secondaryContainerColor


class ListTopPanel(MDTopAppBar):
    def __init__(self):
        self.on_chat_added = None
        self.on_settings_clicked = None
        super().__init__(
            MDTopAppBarLeadingButtonContainer(
                MDActionTopAppBarButton(
                    icon='plus',
                    on_release=lambda x: None if self.on_chat_added is None else self.on_chat_added())
            ),
            MDTopAppBarTitle(text='Chats'),
            MDTopAppBarTrailingButtonContainer(
                MDActionTopAppBarButton(
                    icon='dots-horizontal',
                    on_release=lambda x: None if self.on_settings_clicked is None else self.on_settings_clicked())
            ))
        self.theme_bg_color = 'Custom'
