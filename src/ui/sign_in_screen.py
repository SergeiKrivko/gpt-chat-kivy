from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDTextButton


class SignInScreen(MDScreen):
    def __init__(self, app: MDApp):
        super().__init__(name='SignIn')
        self.app = app

        main_layout = MDBoxLayout(orientation='vertical')
        self.add_widget(main_layout)

        self.top_bar = MDTopAppBar(title='Authorization')
        # self.top_bar.left_action_items = [['arrow-left', lambda x: self.on_closed()]]
        main_layout.add_widget(self.top_bar)

        layout = MDBoxLayout(orientation='vertical', adaptive_height=True)
        layout.padding = dp(20)
        layout.spacing = dp(20)
        main_layout.add_widget(layout)

        self._email_edit = MDTextField(hint_text='Email')
        layout.add_widget(self._email_edit)

        self._password_edit = MDTextField(hint_text='Password', password=True, password_mask='•')
        layout.add_widget(self._password_edit)

        self._button_sign_in = MDTextButton(text='Sign in', style='fill', size_hint_x=0.6, center_x=0.5)
        layout.add_widget(self._button_sign_in)

        main_layout.add_widget(MDBoxLayout())
