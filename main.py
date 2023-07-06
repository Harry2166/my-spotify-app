from __future__ import annotations
from config import CLIENT_ID, CLIENT_SECRET
from dataclasses import dataclass, field
from flet.auth.oauth_provider import OAuthProvider
from flet.auth.authorization import Authorization

import flet as ft
import asyncio
import aiohttp
import base64

REDIRECT_URL = "http://localhost/api/oauth/redirect"

class MyAuthorization(Authorization):
    def __init__(self, *args, **kwargs):
        super(MyAuthorization, self).__init__(*args, **kwargs)

    def _Authorization__get_default_headers(self):
        username = CLIENT_ID
        encoded = base64.b64encode(f'{username}:'.encode('utf8')).decode('utf8')

        return {"User-Agent": f"Flet/0.6.2", "Authorization": f"Basic {encoded}", }
    
@dataclass
class App:
    page: ft.Page
    login_btn : ft.ElevatedButton = field(init=False)
    logout_btn : ft.ElevatedButton = field(init=False)
    provider = OAuthProvider(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_scopes=["playlist-read-private"],
            redirect_url=REDIRECT_URL,
            authorization_endpoint="https://accounts.spotify.com/authorize?",
            token_endpoint="https://accounts.spotify.com/api/token"
        )

    async def login_click(self,e):
        print("You pressed login")
        await self.page.login_async(self.provider, authorization=MyAuthorization)

    async def logout_click(self,e):
        print("You pressed logout")
        await self.page.clean_async()
        await self.page.logout_async()

    async def login_screen(self):
        self.login_btn = ft.ElevatedButton(text="log in", on_click=self.login_click)

        controls = [
            self.login_btn
        ]
        await self.page.add_async(*controls)

    async def main_page(self):

        filler_text = ft.Text("Hello There!")
        self.logout_btn = ft.ElevatedButton("logout", on_click=self.logout_click)

        controls = [
            filler_text,
            self.logout_btn
        ]

        await self.page.add_async(*controls)
    
    async def switching_to_main(self):
        await self.page.clean_async()
        await App(self.page).main_page()

    @classmethod
    async def default(cls, page: ft.Page) -> App:
        return App(
            page=page
        )

    @classmethod
    async def main(cls, page: ft.Page):

        async def on_login(e):
            print("you got in")
            await App(page).switching_to_main()

        async def on_logout(e):
            print("you got out")
            await App(page).login_screen()

        page.on_login = on_login
        page.on_logout = on_logout
        await App(page).login_screen()

ft.app(target=App.main,port=80, view=ft.WEB_BROWSER)