import asyncio

from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.material_resources import dp
from kivymd.uix.bottomsheet import MDBottomSheet, MDBottomSheetContent
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar

from src.chat.chat_bubble import ChatBubble
from src.gpt import async_response, simple_response
from src.gpt.chat import GPTChat
from src.gpt.message import GPTMessage


class ChatWidget(MDScreen):
    def __init__(self, app: MDApp, sm, chat: GPTChat):
        super().__init__(name=f'Chat{chat.id}')
        self.chat = chat
        self.app = app
        self.sm = sm
        self.temp_dir = self.sm.temp_dir

        main_layout = MDBoxLayout(orientation='vertical')
        self.add_widget(main_layout)

        self.top_panel = ChatTopPanel(self.chat)
        main_layout.add_widget(self.top_panel)

        self.scroll_view = CustomScrollView()
        main_layout.add_widget(self.scroll_view)

        self.scroll_layout = MDBoxLayout(orientation='vertical')
        self.scroll_layout.size_hint_y = None
        self.scroll_layout.padding = dp(10)
        self.scroll_layout.spacing = dp(8)
        self.scroll_layout.bind(minimum_height=self._on_resize)
        self.scroll_view.add_widget(self.scroll_layout)
        self.scroll_view.on_scroll = self.on_scroll
        self._bubbles_list = []
        self._bubbles = dict()
        self._to_bottom = True
        self.scroll_view.scroll_y = 0
        self._last_height = 0

        bottom_layout = MDBoxLayout(size_hint_y=None, adaptive_height=True)
        bottom_layout.padding = (dp(15), dp(15), dp(15), dp(25))
        bottom_layout.spacing = dp(10)
        bottom_layout.md_bg_color = app.theme_cls.primary_color
        main_layout.add_widget(bottom_layout)

        self.input_area = MDTextField(
            multiline=True,
            hint_text='Сообщение',
            mode="rectangle",
            size_hint_y=None,
            # padding=4,
        )
        self.input_area.text_color_normal = self.app.theme_cls.bg_normal
        self.input_area.text_color_focus = self.app.theme_cls.bg_normal
        self.input_area.hint_text_color_normal = self.app.theme_cls.bg_normal
        self.input_area.hint_text_color_focus = self.app.theme_cls.bg_normal
        self.input_area.line_color_normal = self.app.theme_cls.primary_color
        self.input_area.line_color_focus = self.app.theme_cls.bg_normal
        bottom_layout.add_widget(self.input_area)

        def on_start(*args):
            self._bottom_sheet = _MessageOptionsPanel(self.app, self, self.chat)
            self._bottom_sheet.on_delete = self.delete_message
            self._bottom_sheet.on_markdown_copy = lambda message: Clipboard.copy(message.content)
        Clock.schedule_once(on_start, 2)

        self.button_send = MDIconButton(icon='send')
        self.button_send.bind(on_release=self.send_message)
        bottom_layout.add_widget(self.button_send)

    def _on_resize(self, instance, height):
        self.scroll_layout.setter('height')(instance, height)
        self.scroll_view.scroll_y = self.scroll_view.scroll_y * self._last_height / self.scroll_layout.height
        self._last_height = self.scroll_layout.height

    def on_scroll(self):
        self._to_bottom = self.scroll_view.scroll_y * self.scroll_layout.height < 50
        self._last_height = self.scroll_layout.height
        if (1 - self.scroll_view.scroll_y) * self.scroll_layout.height < 100:
            self.load_messages()

    def load_messages(self):
        for message in self.chat.load_messages():
            self.insert_bubble(message)

    def add_bubble(self, message: GPTMessage):
        bubble = ChatBubble(self.app, self.temp_dir, message)
        self._bubbles[message.id] = bubble
        self._bubbles_list.append(bubble)
        bubble.on_menu = lambda: self._bottom_sheet.open_message(message)
        self.scroll_layout.add_widget(bubble)
        self._last_height = self.scroll_layout.height
        return bubble

    def insert_bubble(self, message: GPTMessage):
        bubble = ChatBubble(self.app, self.temp_dir, message)
        self._bubbles[message.id] = bubble
        self._bubbles_list.insert(0, bubble)
        bubble.on_menu = lambda: self._bottom_sheet.open_message(message)
        self.scroll_layout.clear_widgets()
        for el in self._bubbles_list:
            self.scroll_layout.add_widget(el)
        if self._to_bottom:
            self.scroll_view.scroll_y = 0
        self._last_height = self.scroll_layout.height
        return bubble

    def new_message(self, role, content):
        message = self.chat.add_message(role, content)
        return self.add_bubble(message)

    def send_message(self, *args):
        if self.input_area.text.strip():
            self.new_message('user', self.input_area.text)
            self.input_area.text = ''

            messages = self.chat.messages_to_prompt([])
            loop = asyncio.get_event_loop()
            loop.create_task(self._send_message(messages)).done()

    async def _send_message(self, messages):
        try:
            if self.sm.get('async'):
                task = asyncio.create_task(async_response(messages))
                await task
                text = task.result()
            else:
                text = simple_response(messages)
            print(f"Success: {repr(text)}")
            self.new_message('assistant', text)
        except Exception as ex:
            print(f"Error: {ex.__class__.__name__}: {ex}")
            MDSnackbar(
                MDLabel(
                    text=f"Error: {ex.__class__.__name__}",
                ),
                y=dp(100),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            ).open()

    def delete_message(self, message):
        bubble = self._bubbles.pop(message.id)
        self._bubbles_list.remove(bubble)
        self.chat.delete_message(message.id)
        self.scroll_layout.clear_widgets()
        for el in self._bubbles_list:
            self.scroll_layout.add_widget(el)


class CustomScrollView(MDScrollView):
    def on_scroll_move(self, touch):
        super().on_scroll_move(touch)
        if hasattr(self, 'on_scroll'):
            self.on_scroll()


class ChatTopPanel(MDTopAppBar):
    def __init__(self, chat: GPTChat):
        super().__init__()
        self.title = chat.name if chat.name else 'Chat'
        self.left_action_items = [['arrow-left', self.close_chat]]
        self.right_action_items = [['dots-horizontal', lambda x: self.on_settings_clicked()]]

        self.on_chat_closed = None

    def close_chat(self, *args):
        if self.on_chat_closed is not None:
            self.on_chat_closed()


class _MessageOptionsPanel(MDBottomSheet):
    def __init__(self, app: MDApp, parent: MDScreen, chat: GPTChat):
        super().__init__(size_hint_y=None, type='modal')
        self._chat = chat
        self._parent = parent
        self.bg_color = app.theme_cls.bg_light

        content = MDBottomSheetContent()
        content.padding = [0, dp(16), 0, 0]
        self.add_widget(content)
        layout = MDBoxLayout(orientation='vertical', padding=[0, dp(20), 0, 0])
        content.add_widget(layout)

        self._label = MDLabel(adaptive_height=True, valign='top', padding=dp(15))
        layout.add_widget(sv := MDScrollView(self._label, size_hint_y=None))

        md_list = MDList()
        layout.add_widget(md_list)

        self.on_delete = None
        self.on_reply = None
        self.on_copy = None
        self.on_markdown_copy = None
        self._message = None

        md_list.add_widget(OneLineIconListItem(
            IconLeftWidget(icon='delete'),
            text='Delete',
            on_press=lambda x: self._on_delete(),
            _no_ripple_effect=True))
        md_list.add_widget(OneLineIconListItem(
            IconLeftWidget(icon='reply'),
            text='Reply',
            on_press=lambda x: self._on_reply(),
            _no_ripple_effect=True))
        md_list.add_widget(OneLineIconListItem(
            IconLeftWidget(icon='content-copy'),
            text='Copy',
            on_press=lambda x: self._on_copy(),
            _no_ripple_effect=True))
        md_list.add_widget(OneLineIconListItem(
            IconLeftWidget(icon='language-markdown'),
            text='Copy as Markdown',
            on_press=lambda x: self._on_markdown_copy(),
            _no_ripple_effect=True))

        height = Window.height - dp(150)
        self.default_opening_height = height
        self.height = height
        sv.height = height - (dp(48) * 4 + dp(12))
        md_list.size_hint_y = None
        md_list.height = dp(48) * 4 + dp(12)

        self._parent.add_widget(self)

    def _on_delete(self):
        self.dismiss()
        if self.on_delete:
            self.on_delete(self._message)

    def _on_reply(self):
        self.dismiss()
        if self.on_reply:
            self.on_reply(self._message)

    def _on_copy(self):
        self.dismiss()
        if self.on_copy:
            self.on_copy(self._message)

    def _on_markdown_copy(self):
        self.dismiss()
        if self.on_markdown_copy:
            self.on_markdown_copy(self._message)

    def open_message(self, message: GPTMessage):
        self._message = message
        self._label.text = message.content
        self.open()
