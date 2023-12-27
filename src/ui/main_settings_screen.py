from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDSeparator
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar

# from src.ui.switch_item import SwitchItem


class MainSettingsScreen(MDScreen):
    def __init__(self, app: MDApp):
        super().__init__(name='Settings')
        self.app = app

        main_layout = MDBoxLayout(orientation='vertical')
        self.add_widget(main_layout)

        self.top_bar = MDTopAppBar(title='Settings')
        self.top_bar.left_action_items = [['arrow-left', lambda x: self.on_closed()]]
        main_layout.add_widget(self.top_bar)

        layout = MDBoxLayout(orientation='vertical')
        layout.padding = 10
        main_layout.add_widget(layout)

        # self.dark_theme_item = SwitchItem("Dark theme")
        # self.dark_theme_item.on_state_changed = self.set_dark_theme
        # layout.add_widget(self.dark_theme_item)
        #
        # layout.add_widget(MDSeparator())
        #
        # self.color_box = SwitchItem("Color")
        # layout.add_widget(self.color_box)

    def set_dark_theme(self, dark):
        # self.app.theme_cls.theme_style = 'Dark' if dark else 'Light'
        pass
