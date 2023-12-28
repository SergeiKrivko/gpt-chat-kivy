from kivymd.app import MDApp
from kivymd.material_resources import dp
from kivymd.uix.bottomsheet import MDBottomSheet, MDListBottomSheet
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRectangleFlatButton, MDTextButton, MDFillRoundFlatButton
from kivymd.uix.list import MDList, OneLineListItem


class SelectionItem(MDBoxLayout):
    def __init__(self, name, values: list[str], current=''):
        super().__init__()
        self._values = values
        self._current = current
        self.adaptive_height = True
        self.padding = 10

        self.label = MDLabel(text=name)
        self.label.padding = 12
        self.label.adaptive_height = True
        self.add_widget(self.label)

        self.button = MDFillRoundFlatButton(text=current)
        # self.button.line_color = (0, 0, 0, 0)
        self.button.bind(on_release=self._on_clicked)
        self.add_widget(self.button)

        self.on_current_changed = None

    def _on_clicked(self, *args):
        bottom_sheet_menu = MDListBottomSheet()
        for el in self._values:
            bottom_sheet_menu.add_item(el, lambda x, y=el: self._set_current(y))
        bottom_sheet_menu.open()

    def _set_current(self, text):
        self._current = text
        self.button.text = text
        if self.on_current_changed:
            self.on_current_changed(text)

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, text):
        self._set_current(text)


class SelectArea(MDListBottomSheet):
    def __init__(self, app: MDApp, values: list[str]):
        super().__init__()
        self.app = app
        self.size_hint_y = None
        self.type = 'standard'
        self.height = dp(20)

        self.bg_color = 'grey'

        for el in values:
            self._add_item(el)

        self.on_selected = None

    def show(self):
        self.open()

    def _add_item(self, text):
        self.add_item(text, lambda *args: self._on_selected(text))

    def _on_selected(self, text):
        print(f"selected \"{text}\"")
        self.dismiss()
        if self.on_selected is not None:
            self.on_selected(text)

