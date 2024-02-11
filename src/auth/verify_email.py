import asyncio
import json

import aiohttp
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.appbar import MDTopAppBar, MDTopAppBarTitle, MDTopAppBarLeadingButtonContainer, MDActionTopAppBarButton

from src import config
from src.commands import async_slot


class VerifyEmailScreen(MDScreen):
    def __init__(self, app: MDApp, sm):
        super().__init__(name='VerifyEmail')
        self._sm = sm
        self.app = app
        self.on_verified = None
        self.on_close = None
        self._email_waiting = False
        self.theme_bg_color = 'Custom'

        self.top_bar = MDTopAppBar(MDTopAppBarTitle(text='Email verification'),
                                   MDTopAppBarLeadingButtonContainer(
                                       MDActionTopAppBarButton(
                                           icon='arrow-left',
                                           on_release=lambda x: self.close())
                                   ), theme_bg_color='Custom')
        self.add_widget(self.top_bar)

        main_layout = MDBoxLayout(orientation='vertical')
        self.add_widget(main_layout)

        layout = MDBoxLayout(orientation='vertical', adaptive_height=True, center_y=0.5)
        layout.padding = dp(20)
        layout.spacing = dp(20)
        main_layout.add_widget(layout)

        self._label = MDLabel(padding=[dp(20), dp(20)])
        main_layout.add_widget(self._label)

        main_layout.add_widget(MDBoxLayout())

    def update_user(self):
        self._label.text = f"To your email address {self._sm.get('user_email')} an email has been sent. " \
                           f"Click on the link in this email to confirm the email address"
        self.send_email_verification()
        self.wait_while_email_verified()

    @async_slot
    async def send_email_verification(self):
        request_ref = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key={config.FIREBASE_API_KEY}"
        data = json.dumps({"requestType": "VERIFY_EMAIL", "idToken": self._sm.get('user_token')})
        async with aiohttp.ClientSession() as session:
            async with session.post(request_ref, data=data) as resp:
                await resp.text()
                if not resp.ok:
                    print(resp.text)

    @staticmethod
    async def get_account_info(id_token):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo?key={0}".format(
            config.FIREBASE_API_KEY)
        data = json.dumps({"idToken": id_token})
        async with aiohttp.ClientSession() as session:
            async with session.post(request_ref, data=data) as resp:
                res = await resp.text()
                if not resp.ok:
                    raise aiohttp.ClientConnectionError
        return json.loads(res)

    @staticmethod
    async def check_email_verified(id_token):
        info = await VerifyEmailScreen.get_account_info(id_token)
        try:
            return info['users'][0]['emailVerified']
        except KeyError:
            return False

    @async_slot
    async def wait_while_email_verified(self):
        id_token = self._sm.get('user_token')
        self._email_waiting = True
        while self._email_waiting:
            await asyncio.sleep(2)
            verified = await self.check_email_verified(id_token)
            if verified:
                self.on_verified()
                return True
        return False

    def close(self):
        self._email_waiting = False
        self.on_close()

    def set_theme(self):
        self.md_bg_color = self.theme_cls.backgroundColor
        self.top_bar.md_bg_color = self.theme_cls.primaryContainerColor
