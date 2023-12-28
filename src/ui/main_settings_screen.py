from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDSeparator
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar

from src.ui.select_area import SelectionItem
from src.ui.switch_item import SwitchItem


class MainSettingsScreen(MDScreen):
    def __init__(self, app: MDApp, sm):
        super().__init__(name='Settings')
        self.app = app
        self.sm = sm

        main_layout = MDBoxLayout(orientation='vertical')
        self.add_widget(main_layout)

        self.top_bar = MDTopAppBar(title='Settings')
        self.top_bar.left_action_items = [['arrow-left', lambda x: self.on_closed()]]
        main_layout.add_widget(self.top_bar)

        layout = MDBoxLayout(orientation='vertical', adaptive_height=True)
        layout.padding = (40, 20, 40, 40)
        main_layout.add_widget(layout)

        self.dark_theme_item = SwitchItem("Dark theme")
        self.dark_theme_item.set_state(self.sm.get('dark', True))
        self.dark_theme_item.on_state_changed = self.set_dark_theme
        layout.add_widget(self.dark_theme_item)

        layout.add_widget(MDSeparator())

        self.color_box = SelectionItem("Color", ['Blue', 'Green', 'Red', 'Pink', 'Yellow', 'Orange'],
                                       self.sm.get('theme', 'Blue'))
        self.color_box.on_current_changed = self.set_theme_color
        layout.add_widget(self.color_box)

        layout.add_widget(MDSeparator())

        main_layout.add_widget(MDBoxLayout())

    def set_dark_theme(self, dark):
        self.sm.set('dark', dark)

    def set_theme_color(self, color):
        self.sm.set('theme', color)
