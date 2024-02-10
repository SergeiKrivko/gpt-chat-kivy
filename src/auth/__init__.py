from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from src.auth.sign_in_screen import SignInScreen
from src.auth.sign_up_screen import SignUpScreen
from src.auth.verify_email import VerifyEmailScreen
from src.commands import async_slot


class AuthManager:
    def __init__(self, app: MDApp, sm, screen_manager: MDScreenManager):
        self._app = app
        self._sm = sm
        self._screen_manager = screen_manager
        self.on_auth = None

        self._sign_in_screen = SignInScreen(self._app, self._sm)
        self._sign_in_screen.on_sign_in = self._on_auth
        self._sign_in_screen.on_sign_up = lambda *args: self._set_screen('SignUp')
        self._screen_manager.add_widget(self._sign_in_screen)
        if not self._sm.get('user_id'):
            self._screen_manager.current = 'SignIn'

        self._sign_up_screen = SignUpScreen(self._app, self._sm)
        self._sign_up_screen.on_sign_up = self._on_auth
        self._sign_up_screen.on_closed = lambda *args: self._set_screen('SignIn')
        self._screen_manager.add_widget(self._sign_up_screen)

        self._verify_email_screen = VerifyEmailScreen(self._app, self._sm)
        self._verify_email_screen.on_verified = self._on_auth
        self._verify_email_screen.on_closed = lambda *args: self._set_screen('SignIn')
        self._screen_manager.add_widget(self._verify_email_screen)

    @async_slot
    async def _on_auth(self):
        email_verified = await VerifyEmailScreen.check_email_verified(self._sm.get('user_token'))
        if email_verified:
            self.on_auth()
        else:
            self._verify_email_screen.update_user()
            self._set_screen('VerifyEmail')

    def _on_email_verified(self):
        self.on_auth()

    def _set_screen(self, screen):
        if screen == 'SignIn':
            self._screen_manager.transition.direction = 'right'
        else:
            self._screen_manager.transition.direction = 'left'
        self._screen_manager.current = screen
