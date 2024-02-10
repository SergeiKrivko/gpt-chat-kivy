from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from src.auth.sign_in_screen import SignInScreen


class AuthManager:
    def __init__(self, app: MDApp, sm, screen_manager: MDScreenManager):
        self._app = app
        self._sm = sm
        self._screen_manager = screen_manager
        self.on_auth = None

        self._sign_in_screen = SignInScreen(self._app, self._sm)
        self._sign_in_screen.on_sign_in = self._on_auth
        self._screen_manager.add_widget(self._sign_in_screen)
        if not self._sm.get('user_id'):
            self._screen_manager.current = 'SignIn'

    def _on_auth(self):
        self.on_auth()
