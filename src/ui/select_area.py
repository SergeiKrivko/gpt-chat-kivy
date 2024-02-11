from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.material_resources import dp
from kivymd.uix.bottomsheet import MDBottomSheet, MDBottomSheetDragHandle
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText
from kivymd.uix.scrollview import MDScrollView


class SelectionItem(MDBoxLayout):
    def __init__(self, parent, name, values: list[str], current=''):
        super().__init__()
        self._values = values
        self._current = current
        self._parent = parent
        self.adaptive_height = True

        self.label = MDLabel(text=name)
        self.label.adaptive_height = True
        self.add_widget(self.label)

        self.button = MDButton(button_text := MDButtonText(text=current))
        self._button_text = button_text
        # self.button.line_color = (0, 0, 0, 0)
        self.button.bind(on_release=self._on_clicked)
        self.add_widget(self.button)

        self.on_current_changed = None

        self._bottom_sheet = BottomSheet(values)
        self._bottom_sheet.on_item_selected = self._set_current
        parent.add_widget(self._bottom_sheet)

    def _on_clicked(self, *args):
        self._bottom_sheet.set_state('open')

    def _set_current(self, text):
        self._bottom_sheet.set_state('close')
        self._current = text
        self._button_text.text = text
        if self.on_current_changed:
            self.on_current_changed(text)

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, text):
        self._set_current(text)

    def set_theme(self):
        self._bottom_sheet.set_theme()


class BottomSheet(MDBottomSheet):
    def __init__(self, values):
        self._items = [
            MDListItem(
                MDListItemHeadlineText(text=el),
                on_release=lambda x, value=el: self.on_item_selected(value),
                theme_bg_color='Custom'
            ) for el in values
        ]
        super().__init__(
            MDBoxLayout(
                MDScrollView(
                    MDList(*self._items),
                ),
            ),
            size_hint_y=0.7,
            sheet_type='modal',
        )
        self.swipe_distance = 10000

    def set_theme(self):
        for el in self._items:
            el.bg_color = self.theme_cls.surfaceColor
