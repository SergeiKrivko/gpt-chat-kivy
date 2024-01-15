from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.material_resources import dp
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.uix.bottomsheet.bottomsheet import MDBottomSheet, MDBottomSheetContent
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineIconListItem, OneLineListItem, MDList
from kivymd.uix.scrollview import MDScrollView


class SelectionItem(MDBoxLayout):
    def __init__(self, parent, name, values: list[str], current=''):
        super().__init__()
        self._values = values
        self._current = current
        self._parent = parent
        self.adaptive_height = True

        self.label = MDLabel(text=name)
        self.label.padding = dp(12)
        self.label.adaptive_height = True
        self.add_widget(self.label)

        self.button = MDFillRoundFlatButton(text=current)
        # self.button.line_color = (0, 0, 0, 0)
        self.button.bind(on_release=self._on_clicked)
        self.add_widget(self.button)

        self.on_current_changed = None

        # def on_start(self):
        def on_start(*args):
            bottom_sheet = MDBottomSheet(
                id="bottom_sheet",
                size_hint_y=None,
                bg_color="grey",
            )
            self._bottom_sheet = bottom_sheet

            content = MDBottomSheetContent()
            content.padding = [0, dp(16), 0, 0]
            bottom_sheet.add_widget(content)
            md_list = MDList(adaptive_height=True)
            content.add_widget(sv := MDScrollView(md_list))
            for el in self._values:
                md_list.add_widget(OneLineListItem(
                    text=el,
                    on_release=lambda x, y=el: self._set_current(y),
                    _no_ripple_effect=True))

            self._parent.add_widget(bottom_sheet)
            height = min(Window.height - dp(150), dp(48) * len(self._values) + dp(12))
            bottom_sheet.default_opening_height = height
            bottom_sheet.height = height
            sv.size_hint_y = None
            sv.height = height - dp(12)

        Clock.schedule_once(on_start, 2)

    def _on_clicked(self, *args):
        self._bottom_sheet.open()

    def _set_current(self, text):
        self._bottom_sheet.dismiss()
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
