import asyncio

from kivy.metrics import dp
from kivy.utils import hex_colormap
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.appbar import MDTopAppBar, MDTopAppBarTitle, MDTopAppBarLeadingButtonContainer, MDActionTopAppBarButton

from src.ui.select_area import SelectionItem
from src.ui.switch_item import SwitchItem


class MainSettingsScreen(MDScreen):
    def __init__(self, app: MDApp, sm):
        super().__init__(name='Settings')
        self.app = app
        self.sm = sm
        self.on_account_exit = None
        self.theme_bg_color = 'Custom'

        main_layout = MDBoxLayout(orientation='vertical')
        self.add_widget(main_layout)

        self.top_bar = MDTopAppBar(
            MDTopAppBarLeadingButtonContainer(
                MDActionTopAppBarButton(icon='arrow-left', on_release=lambda x: self.on_closed())
            ),
            MDTopAppBarTitle(text='Settings'),
            theme_bg_color='Custom',
        )
        main_layout.add_widget(self.top_bar)

        layout = MDBoxLayout(orientation='vertical', adaptive_height=True)
        layout.padding = dp(20)
        layout.spacing = dp(15)
        main_layout.add_widget(layout)

        self.dark_theme_item = SwitchItem("Dark theme")
        self.dark_theme_item.set_state(self.sm.get('dark', True))
        self.dark_theme_item.on_state_changed = self.set_dark_theme
        layout.add_widget(self.dark_theme_item)

        layout.add_widget(MDDivider())

        self.color_box = SelectionItem(self, "Color", [name_color.capitalize() for name_color in hex_colormap.keys()],
                                       self.sm.get('theme', 'Blue'))
        self.color_box.on_current_changed = self.set_theme_color
        layout.add_widget(self.color_box)

        layout.add_widget(MDDivider())

        self.async_item = SwitchItem("Async")
        self.async_item.set_state(self.sm.get('async', True))
        self.async_item.on_state_changed = self.set_async
        layout.add_widget(self.async_item)

        layout.add_widget(MDDivider())

        email_layout = MDBoxLayout(adaptive_height=True)
        layout.add_widget(email_layout)

        self._email_label = MDLabel()
        email_layout.add_widget(self._email_label)

        self._exit_account_button = MDButton(MDButtonText(text='Exit'), on_release=lambda *args: self.on_account_exit())
        email_layout.add_widget(self._exit_account_button)

        main_layout.add_widget(MDBoxLayout())

    def update_user(self):
        self._email_label.text = self.sm.get('user_email')

    def set_dark_theme(self, dark):
        self.sm.set('dark', dark)
        self.theme_cls.switch_theme()
        self.on_color_changed()

    def set_async(self, dark):
        self.sm.set('async', dark)

    def set_theme_color(self, color):
        self.theme_cls.primary_palette = color
        self.sm.set('theme', color)
        self.on_color_changed()

    def set_theme(self):
        self.color_box.set_theme()
        self.md_bg_color = self.app.theme_cls.backgroundColor
        self.top_bar.md_bg_color = self.app.theme_cls.primaryContainerColor
