import asyncio

from kivymd.app import MDApp
from kivymd.material_resources import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
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
        self.scroll_layout.add_widget(bubble)
        self._last_height = self.scroll_layout.height
        return bubble

    def insert_bubble(self, message: GPTMessage):
        bubble = ChatBubble(self.app, self.temp_dir, message)
        self._bubbles[message.id] = bubble
        self._bubbles_list.insert(0, bubble)
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
