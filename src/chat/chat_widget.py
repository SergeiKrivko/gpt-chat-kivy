import asyncio

from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.material_resources import dp
from kivymd.uix.bottomsheet import MDBottomSheet
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, MDListItem, MDListItemLeadingIcon, MDListItemHeadlineText
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.appbar import MDTopAppBar, MDTopAppBarTitle, MDTopAppBarLeadingButtonContainer, \
    MDTopAppBarTrailingButtonContainer, MDActionTopAppBarButton

from src.chat.chat_bubble import ChatBubble
from src.commands import async_slot
from src.database import ChatManager
from src.gpt import async_response, simple_response
from src.gpt.chat import GPTChat
from src.gpt.message import GPTMessage
from src.ui.chat_input_area import ChatInputArea


class ChatWidget(MDScreen):
    def __init__(self, app: MDApp, sm, chat_manager: ChatManager, chat: GPTChat):
        super().__init__(name=f'Chat{chat.id}')
        self.chat = chat
        self.app = app
        self.sm = sm
        self.theme_bg_color = 'Custom'
        self._chat_manager = chat_manager
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

        self._bottom_layout = MDBoxLayout(size_hint_y=None, adaptive_height=True, theme_bg_color='Custom')
        self._bottom_layout.padding = (dp(15), dp(15), dp(15), dp(25))
        self._bottom_layout.spacing = dp(10)
        main_layout.add_widget(self._bottom_layout)

        self.input_area = ChatInputArea(self.app)
        self._bottom_layout.add_widget(self.input_area)

        self._bottom_sheet = _MessageOptionsPanel(self.app, self, self.chat)
        self._bottom_sheet.on_delete = self.delete_message
        self._bottom_sheet.on_markdown_copy = lambda message: Clipboard.copy(message.content)

        self.button_send = MDIconButton(icon='send')
        self.button_send.bind(on_release=self._send_message)
        self._bottom_layout.add_widget(self.button_send)

        # self._button_down = MDIconButton(icon='down_arrow', parent=self,
        #                                  pos=[self.width - dp(50), self.height - dp(150)])

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

    @async_slot
    async def _send_message(self, messages):
        if not self.input_area.text.strip():
            return

        status = await self._chat_manager.new_message(self.chat.id, 'user', self.input_area.text)
        if not status:
            return
        messages = self.chat.messages_to_prompt([])
        self.input_area.text = ''

        try:
            if self.sm.get('async'):
                text = await asyncio.create_task(async_response(messages, model=self.chat.model))
            else:
                text = simple_response(messages, model=self.chat.model)
            print(f"Success: {repr(text)}")

            await self._chat_manager.new_message(self.chat.id, 'assistant', text)

        except Exception as ex:
            print(f"Error: {ex.__class__.__name__}: {ex}")
            MDSnackbar(
                MDSnackbarText(
                    text=f"Error: {ex.__class__.__name__}",
                ),
                y=dp(100),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
                theme_bg_color='Custom',
                md_bg_color=self.app.theme_cls.surfaceColor,
            ).open()

    def delete_message(self, message):
        self._chat_manager.delete_message(self.chat.id, message)

    def delete_bubble(self, message):
        bubble = self._bubbles.pop(message.id)
        self._bubbles_list.remove(bubble)
        self.scroll_layout.clear_widgets()
        for el in self._bubbles_list:
            self.scroll_layout.add_widget(el)

    def drop_messages(self):
        y = self.scroll_view.scroll_y * (self.scroll_layout.height - self.scroll_view.height) + self.scroll_view.height
        for el in self._bubbles_list:
            if el.top <= y:
                for message in self.chat.drop_messages(el.message.id):
                    self.delete_bubble(message)
                break

    def set_theme(self):
        self.top_panel.md_bg_color = self.app.theme_cls.primaryContainerColor
        self._bottom_layout.md_bg_color = self.app.theme_cls.primaryContainerColor
        self.md_bg_color = self.app.theme_cls.backgroundColor
        self.input_area.set_theme()
        for bubble in self._bubbles_list:
            bubble.set_theme()


class CustomScrollView(MDScrollView):
    def on_scroll_move(self, touch):
        super().on_scroll_move(touch)
        if hasattr(self, 'on_scroll'):
            self.on_scroll()


class ChatTopPanel(MDTopAppBar):
    def __init__(self, chat: GPTChat):
        super().__init__(
            MDTopAppBarLeadingButtonContainer(
                MDActionTopAppBarButton(
                    icon='arrow-left',
                    on_release=self.close_chat,
                ),

            ),
            MDTopAppBarTitle(text=chat.name or 'Chat'),
            MDTopAppBarTrailingButtonContainer(
                MDActionTopAppBarButton(
                    icon='dots-horizontal',
                    on_release=lambda x: self.on_settings_clicked()
                )
            ),
            theme_bg_color='Custom'
        )

        self.on_chat_closed = None

    def close_chat(self, *args):
        if self.on_chat_closed is not None:
            self.on_chat_closed()


class _MessageOptionsPanel(MDBottomSheet):
    def __init__(self, app: MDApp, parent: MDScreen, chat: GPTChat):
        super().__init__(size_hint_y=0.7, sheet_type='modal', swipe_distance=10000)
        self._chat = chat
        self._parent = parent

        layout = MDBoxLayout(orientation='vertical', padding=[0, dp(10), 0, 0])
        self.add_widget(layout)

        scroll_view = MDScrollView()
        layout.add_widget(scroll_view)

        self._label = MDLabel(valign='top', padding=dp(10), size_hint_y=None, adaptive_height=True)
        scroll_view.add_widget(self._label)

        md_list = MDList()
        layout.add_widget(md_list)

        self.on_delete = None
        self.on_reply = None
        self.on_copy = None
        self.on_markdown_copy = None
        self._message = None

        md_list.add_widget(MDListItem(
            MDListItemLeadingIcon(icon='delete'),
            MDListItemHeadlineText(text='Delete'),
            on_release=lambda x: self._on_delete(),
            ripple_effect=False))
        md_list.add_widget(MDListItem(
            MDListItemLeadingIcon(icon='reply'),
            MDListItemHeadlineText(text='Reply'),
            on_release=lambda x: self._on_reply(),
            ripple_effect=False))
        md_list.add_widget(MDListItem(
            MDListItemLeadingIcon(icon='content-copy'),
            MDListItemHeadlineText(text='Copy'),
            on_release=lambda x: self._on_copy(),
            ripple_effect=False))
        md_list.add_widget(MDListItem(
            MDListItemLeadingIcon(icon='language-markdown'),
            MDListItemHeadlineText(text='Copy as Markdown'),
            on_release=lambda x: self._on_markdown_copy(),
            ripple_effect=False
        ))

        height = Window.height - dp(150)
        self.default_opening_height = height
        self.height = height
        self._label.height = height - (dp(48) * 4 + dp(12))
        md_list.size_hint_y = None
        md_list.height = dp(48) * 4 + dp(12)

        self._parent.add_widget(self)

    def _on_delete(self):
        self.set_state('close')
        if self.on_delete:
            self.on_delete(self._message)

    def _on_reply(self):
        self.set_state('close')
        if self.on_reply:
            self.on_reply(self._message)

    def _on_copy(self):
        self.set_state('close')
        if self.on_copy:
            self.on_copy(self._message)

    def _on_markdown_copy(self):
        self.set_state('close')
        if self.on_markdown_copy:
            self.on_markdown_copy(self._message)

    def open_message(self, message: GPTMessage):
        self._message = message
        self._label.text = message.content
        if not self._label.text:
            self._label.text = '<Empty>'
        self.set_state('open')
