from kivymd.app import MDApp
from kivymd.material_resources import dp
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.uix.bottomsheet.bottomsheet import ListBottomSheetIconLeft
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineIconListItem, OneLineListItem


class SelectionItem(MDBoxLayout):
    def __init__(self, name, values: list[str], current=''):
        super().__init__()
        self._values = values
        self._current = current
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

    def _on_clicked(self, *args):
        bottom_sheet_menu = MDListBottomSheet()
        try:
            bottom_sheet_menu.add_item = _add_item
            for el in self._values:
                bottom_sheet_menu.add_item(bottom_sheet_menu, el, lambda x, y=el: self._set_current(y))
        except Exception as ex:
            print(f"{ex.__class__.__name__}: {ex}")
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


def _add_item(self, text, callback, icon=None):
    """
    :arg text: element text;
    :arg callback: function that will be called when clicking on an item;
    :arg icon: which will be used as an icon to the left of the item;
    """

    if icon:
        item = OneLineIconListItem(text=text, on_release=callback)
        item.add_widget(ListBottomSheetIconLeft(icon=icon))
    else:
        item = OneLineListItem(text=text, on_release=callback)
    item.bind(on_release=lambda x: self.dismiss())
    self.sheet_list.ids.box_sheet_list.add_widget(item)


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

