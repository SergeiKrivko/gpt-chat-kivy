from typing import Union

from kivy.metrics import dp
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.slider import MDSlider, MDSliderHandle, MDSliderValueLabel
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.appbar import MDTopAppBar, MDTopAppBarTitle, MDTopAppBarLeadingButtonContainer, MDActionTopAppBarButton

import g4f
from src.gpt.chat import GPTChat
from src.ui.select_area import SelectionItem
from src.ui.switch_item import SwitchItem


class ChatSettingsScreen(MDScreen):
    def __init__(self, app: MDApp, chat_manager):
        super().__init__(name='ChatSettings')
        self.app = app
        self._chat_manager = chat_manager
        self.theme_bg_color = 'Custom'

        main_layout = MDBoxLayout(orientation='vertical')
        self.add_widget(main_layout)

        self.top_bar = MDTopAppBar(
            MDTopAppBarLeadingButtonContainer(
                MDActionTopAppBarButton(icon='arrow-left', on_release=lambda x: self.on_closed())
            ),
            MDTopAppBarTitle(text='Chat settings'),
            theme_bg_color='Custom'
        )
        main_layout.add_widget(self.top_bar)

        scroll_view = MDScrollView()
        main_layout.add_widget(scroll_view)

        layout = MDBoxLayout(orientation='vertical', adaptive_height=True)
        layout.padding = dp(20)
        layout.spacing = dp(15)
        scroll_view.add_widget(layout)

        layout.add_widget(MDLabel(text="Chat name:", adaptive_height=True))
        self.chat_name_edit = MDTextField(mode='outlined', radius=dp(10))
        layout.add_widget(self.chat_name_edit)

        layout.add_widget(MDDivider())

        self.model_edit = SelectionItem(self, "Model", ['default'] + g4f.models.Model.__all__())
        layout.add_widget(self.model_edit)

        layout.add_widget(MDDivider())

        layout.add_widget(MDLabel(text="Used messages:", adaptive_height=True))
        self.used_messages_edit = MDSlider(MDSliderHandle(), MDSliderValueLabel(),
                                           min=1, max=10)
        layout.add_widget(self.used_messages_edit)

        layout.add_widget(MDDivider())

        layout.add_widget(MDLabel(text="Saved messages:", adaptive_height=True))
        self.saved_messages_edit = MDSlider(MDSliderHandle(), MDSliderValueLabel(),
                                            min=50, max=1000)
        layout.add_widget(self.saved_messages_edit)

        layout.add_widget(MDDivider())

        layout.add_widget(MDLabel(text="Temperature:", adaptive_height=True))
        self.temperature_edit = MDSlider(MDSliderHandle(), MDSliderValueLabel(),
                                         min=0, max=100)
        layout.add_widget(self.temperature_edit)

        layout.add_widget(MDDivider())

        self.synchronize_item = SwitchItem("Synchronize")
        layout.add_widget(self.synchronize_item)

        layout.add_widget(MDDivider())

        self._chat: Union[GPTChat, None] = None

    def open_chat(self, chat: GPTChat):
        self._chat = chat

        self.chat_name_edit.text = chat.name if chat.name else ''
        self.model_edit.current = 'default' if not chat.model else chat.model
        self.used_messages_edit.value = chat.used_messages
        self.saved_messages_edit.value = chat.saved_messages
        self.temperature_edit.value = int(chat.temperature * 100)
        self.synchronize_item.set_state(bool(chat.remote_id))

    def save_chat(self):
        if self._chat is None:
            return
        self._chat.name = self.chat_name_edit.text
        self._chat.model = self.model_edit.current
        self._chat.used_messages = self.used_messages_edit.value
        self._chat.saved_messages = self.saved_messages_edit.value
        self._chat.temperature = self.temperature_edit.value / 100
        self._chat_manager.make_remote(self._chat, self.synchronize_item.state)

    def set_theme(self):
        self.md_bg_color = self.app.theme_cls.backgroundColor
        self.top_bar.md_bg_color = self.app.theme_cls.primaryContainerColor
