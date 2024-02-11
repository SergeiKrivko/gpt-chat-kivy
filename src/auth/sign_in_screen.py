import json

import aiohttp
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.appbar import MDTopAppBar, MDTopAppBarTitle

from src import config
from src.commands import async_slot


class SignInScreen(MDScreen):
    def __init__(self, app: MDApp, sm):
        super().__init__(name='SignIn')
        self._sm = sm
        self.app = app
        self.on_sign_in = None
        self.on_sign_up = None
        self.theme_bg_color = 'Custom'

        main_layout = MDBoxLayout(orientation='vertical')
        self.add_widget(main_layout)

        self.top_bar = MDTopAppBar(MDTopAppBarTitle(text='Sign in'), theme_bg_color='Custom')
        main_layout.add_widget(self.top_bar)

        layout = MDBoxLayout(orientation='vertical', adaptive_height=True, center_y=0.5)
        layout.padding = dp(20)
        layout.spacing = dp(20)
        main_layout.add_widget(layout)

        self._email_edit = MDTextField(MDTextFieldHintText(text='Email'), text=self._sm.get('user_email', ''))
        layout.add_widget(self._email_edit)

        self._password_edit = MDTextField(MDTextFieldHintText(text='Password'), password=True, password_mask='•')
        layout.add_widget(self._password_edit)

        self._error_label = MDLabel()
        self._error_label.text_color = self.app.theme_cls.errorColor
        layout.add_widget(self._error_label)

        self._button_sign_in = MDButton(MDButtonText(text='Sign in', theme_font_size='Custom', font_size=dp(28),
                                                     padding=[dp(40), dp(30)]),
                                        width=dp(200), height=dp(50), on_release=self._sign_in, style='filled')
        layout.add_widget(self._button_sign_in)

        self._button_sign_up = MDButton(MDButtonText(text='Sign up'), style='text',
                                        on_release=lambda *args: self.on_sign_up())
        layout.add_widget(self._button_sign_up)

        self._button_reset_password = MDButton(MDButtonText(text='Forget password?'), style='text')
        layout.add_widget(self._button_reset_password)

        main_layout.add_widget(MDBoxLayout())

    def show_error(self, error):
        self._error_label.text = error

    @async_slot
    async def _sign_in(self, *args):
        rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={config.FIREBASE_API_KEY}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(rest_api_url,
                                        data=json.dumps({"email": self._email_edit.text,
                                                         "password": self._password_edit.text,
                                                         "returnSecureToken": True})) as resp:

                    res = await resp.text()
                    res = json.loads(res)
                    if resp.ok:
                        self._sm.set('user_email', res['email'])
                        self._sm.set('user_token', res['idToken'])
                        self._sm.set('user_refresh_token', res['refreshToken'])
                        self._sm.set('user_id', res['localId'])
                        self.on_sign_in()
                    else:
                        error = res.get('error', dict()).get('message')
                        if error == 'INVALID_LOGIN_CREDENTIALS':
                            self.show_error("Неверный логин или пароль")
                        else:
                            self.show_error(f"Неизвестная ошибка: {error}")
                        self._password_edit.text = ""
        except aiohttp.ClientConnectionError:
            self.show_error("Нет подключения к интернету")

    def set_theme(self):
        self.md_bg_color = self.theme_cls.backgroundColor
        self.top_bar.md_bg_color = self.theme_cls.primaryContainerColor
