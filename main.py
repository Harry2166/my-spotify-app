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
BASE_API_URL = "https://accounts.spotify.com/authorize?"

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
            token_endpoint="https://accounts.spotify.com/api/token?" # this one is wrong!! -> will need to figure out the token endpoint for this or else i might have to change
        )
    
    # async def get_access_token(self):
    #     request = aiohttp.request(
    #         method="POST",
    #         url="https://api.spotify.com/v1/me/shows?offset=0&limit=20",
    #         data = {
    #             "grant_type":    "authorization_code",
    #             "code":          code,
    #             "redirect_uri":  REDIRECT_URL,
    #             "client_secret": CLIENT_SECRET,
    #             "client_id":     CLIENT_ID,
    #             },
    #         #params,
    #     )

    # async def get_playlists(self):
    #     access_token = await self.get_access_token()

    #     headers = {
    #         'Authorization': f'Bearer {access_token}'
    #     }

    #     request = aiohttp.request(
    #         method="GET",
    #         url="https://api.spotify.com/v1/me/shows?offset=0&limit=20",
    #         #data,
    #         #params,
    #         headers=headers,
    #     )

    #     async with request as resp:
    #         data = await resp.json()
    #     return data

    async def login_click(self,e):
        print("You pressed login")
        await self.page.login_async(self.provider, authorization=MyAuthorization)

    async def logout_click(self,e):
        print("You pressed logout")
        await self.page.clean_async()
        await self.page.logout_async()

    # async def playlists_click(self,e):
    #     all_playlists = await self.get_playlists()
    #     print(all_playlists)

    async def login_screen(self):
        self.login_btn = ft.ElevatedButton(text="log in", on_click=self.login_click)

        controls = [
            self.login_btn
        ]
        await self.page.add_async(*controls)

    async def main_page(self):

        filler_text = ft.Text("Hello There!")
        self.logout_btn = ft.ElevatedButton("logout", on_click=self.logout_click)
        playlist_btn = ft.ElevatedButton("check playlists", on_click=self.playlists_click)

        controls = [
            filler_text,
            playlist_btn,
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
            if e.error:
                async def close(e):
                    error_warning.open = False
                    await page.update_async()

                error_warning = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("ERROR"),
                    content=ft.Text(f"{e.error}"),
                    actions=[
                        ft.TextButton("Ok", on_click=close),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                    open=True
                )
                await page.add_async(error_warning)
                await page.update_async()
            else:
                await App(page).switch_to_feed()

        async def on_logout(e):
            print("you got out")
            await App(page).login_screen()

        page.on_login = on_login
        page.on_logout = on_logout
        await App(page).login_screen()

ft.app(target=App.main,port=80, view=ft.WEB_BROWSER)