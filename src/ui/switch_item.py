from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDSwitch


class SwitchItem(MDBoxLayout):
    def __init__(self, text):
        super().__init__()
        self.adaptive_height = True
        self.padding = (0, 0, 0, 0)

        self.label = MDLabel(text=text)
        self.label.valign = 'center'
        # self.label.adaptive_height = True
        self.add_widget(self.label)

        self.switch = _Switch()
        self.switch.on_state_changed = self._on_state_changed
        self.add_widget(self.switch)

        self.on_state_changed = None

    def set_state(self, state):
        self.switch.active = state

    @property
    def state(self):
        return self.switch.active

    def _on_state_changed(self, ins, state):
        if self.on_state_changed is not None:
            self.on_state_changed(state)


class _Switch(MDSwitch):
    def __init__(self):
        super().__init__()
        self.on_state_changed = None

    def on_active(self, instance_switch, active_value: bool) -> None:
        super().on_active(instance_switch, active_value)
        if self.on_state_changed is not None:
            self.on_state_changed(instance_switch, active_value)

