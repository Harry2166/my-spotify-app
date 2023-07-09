
from config import CLIENT_ID, CLIENT_SECRET
from requests import post, get
import base64
import json
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from webbrowser import open
from kivymd.app import MDApp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image, AsyncImage
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, OneLineAvatarListItem, ImageLeftWidget

REDIRECT_URL = "https://www.google.com" # -> this worked? LOL
BASE_AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPE = [
        "user-read-email",
        "playlist-read-collaborative",
        "playlist-read-private"
        ]

colors = {
    "Teal": {
        "200": "#212121",
        "500": "#212121",
        "700": "#212121",
    },
    "Red": {
        "200": "#C25554",
        "500": "#C25554",
        "700": "#C25554",
    },
    "Light": {
        "StatusBar": "E0E0E0",
        "AppBar": "#202020",
        "Background": "#2E3032",
        "CardsDialogs": "#FFFFFF",
        "FlatButtonDown": "#CCCCCC",
    },
}

class Spotify:
    def __init__(self):
        self.spotify = OAuth2Session(CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URL)
        self.token = self.get_token()
        self.headers = {"Authorization":f"Bearer {self.get_token()}"}
    
    def authorize(self):
        authorization_url, state = self.spotify.authorization_url(BASE_AUTH_URL)
        open(authorization_url)

    def fetching_token(self, redirect_response):
        auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)

        token = self.spotify.fetch_token(TOKEN_URL, auth=auth,
                authorization_response=redirect_response)
        
        return token
    
    def get_token(self):
        username = f"{CLIENT_ID}:{CLIENT_SECRET}"
        auth_bytes = username.encode("utf-8")
        encoded = str(base64.b64encode(auth_bytes),'utf8')

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization" : f"Basic {encoded}",
            "Content-Type" : "application/x-www-form-urlencoded"
        }
        data = {"grant_type" : "client_credentials"}
        result = post(url, headers=headers, data=data)
        json_result = json.loads(result.content)
        token = json_result["access_token"]
        return token

    def get_spotify_id(self,id,limit=1):
        url = "https://api.spotify.com/v1/search"
        query = f"?q={id}&type=artist&limit={limit}"

        query_url = url + query
        result = self.spotify.get(query_url, headers=self.headers)
        results = json.loads(result.content)  
        return results["artists"]["items"][0]["id"]
    
    def get_artist(self, artist):
        artist_id = self.get_spotify_id(artist)
        url = f"https://api.spotify.com/v1/artists/{artist_id}"

        result = get(url, headers=self.headers)
        results = json.loads(result.content)
        return results

    def get_my_data(self):
        result = self.spotify.get("https://api.spotify.com/v1/me", headers=self.headers)
        results = json.loads(result.content)

        return results
    
    def get_user_playlists(self):
        user_id = self.get_my_data()["id"]
        url = f"https://api.spotify.com/v1/users/{user_id}/playlists?limit=5"
        result = get(url, headers=self.headers)
        results = json.loads(result.content)

        return results
    
spotify = Spotify()

class SpotifyApp(MDApp):
    authorization_data = ""
    profile_data = ""
    controls = []
    playlist_ctrls = {}
    def build(self):
        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.7)
        self.window.pos_hint = {"center_x": 0.5, "center_y":0.5}

        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Red"

        return self.window
    
    def on_start(self):
        self.msg = Label(
            text="Please login to your Spotify and paste the entire URL of the site after your login"
        )
        
        self.authorize_button = Button(
            text="Authorize",
            size_hint= (1,0.5),
            bold= True,
            background_color ='#47B5FF',
            )
        self.authorize_button.bind(on_press=self.authorize_callback)

        self.redirect_url = TextInput(
            multiline=False,
            padding_y= (20,20),
            size_hint= (1, 0.5)
            )

        self.submit_button = Button(
            text="Submit",
            size_hint= (1,0.5),
            bold= True,
            background_color ='#47B5FF',
            )
        self.submit_button.bind(on_press=self.submit_callback)

        self.controls = [
            self.msg,
            self.authorize_button,
            self.redirect_url,
            self.submit_button
        ]

        self.add_widgets()

    def go_to_main_page(self, event):
        self.remove_widgets()
        self.main_page()
    
    def main_page(self):
        name = self.profile_data["display_name"]
        if len(self.profile_data["images"]) == 0:
            pfp_image_url = "https://img.freepik.com/free-icon/user_318-644325.jpg"
        else:
            pfp_image_url = self.profile_data["images"][0]["url"]

        self.profile_picture = AsyncImage(
            source=pfp_image_url,
            )
        self.greeting = Label(
            text=f"Hello {name}!",
        )

        self.playlists_btn = Button(
            text="Playlists",
            size_hint= (1,0.5),
            bold= True,
            background_color ='#47B5FF',
        )
        self.playlists_btn.bind(on_press=self.playlist_callback)

        self.controls = [
            self.profile_picture,
            self.greeting,
            self.playlists_btn
        ]
        self.add_widgets()

    def indiv_playlist(self, event):
        self.remove_widgets()
        self.go_to_indiv_playlist(self.playlist_ctrls[event])

    def go_to_indiv_playlist(self, data):
        # get id of the playlist here
        name_of_playlist = data["name"]
        url = f"https://api.spotify.com/v1/playlists/{data['id']}/tracks"
        result = get(url, headers=spotify.headers)
        results = json.loads(result.content)
        self.indiv_playlist_page(results, name_of_playlist)
    
    def indiv_playlist_page(self, data, name):
        to_be_added_to_controls = MDScrollView()
        md_list = MDList()
        to_be_added_to_controls.add_widget(md_list)

        for track in data["items"]:
            image = track["track"]["album"]["images"][0]["url"]
            item = OneLineAvatarListItem(ImageLeftWidget(source=image), text=track["track"]["name"], theme_text_color="Custom", text_color=(1, 1, 1, 1))
            md_list.add_widget(item)
        self.controls.append(Label(text=name, size_hint=(0.1,0.1)))
        self.controls.append(to_be_added_to_controls)
        self.controls.append(Button(text="Back", on_press=self.playlist_callback, size_hint=(0.2, 0.1)))
        self.add_widgets()

    def playlists_page(self):
        playlist_data = spotify.get_user_playlists()
        all_playlists = playlist_data["items"]

        to_be_added_to_controls = MDScrollView()
        md_list = MDList()
        to_be_added_to_controls.add_widget(md_list)

        for playlist in all_playlists:
            image = playlist["images"][0]["url"]
            item = OneLineAvatarListItem(
                    ImageLeftWidget(source=image),
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1), 
                    text=playlist["name"],
                    on_release = self.indiv_playlist
                )
            self.playlist_ctrls[item] = playlist
            #self.controls.append(item)
            md_list.add_widget(item)

        self.controls.append(to_be_added_to_controls)
        self.controls.append(Button(text="Back", on_press=self.go_to_main_page, size_hint=(0.2, 0.1)))
        self.add_widgets()
    
    def add_widgets(self):
        for elem in self.controls:
            self.window.add_widget(elem)

    def remove_widgets(self):
        for elem in self.controls:
            self.window.remove_widget(elem)
        self.controls = []

    def authorize_callback(self, event):
        spotify.authorize()

    def submit_callback(self, event):
        if self.redirect_url.text == "":
            print("Empty") # make this be a popup
        else:
            self.authorization_data = spotify.fetching_token(self.redirect_url.text)
            self.profile_data = spotify.get_my_data()
            self.remove_widgets()
            self.main_page()

    def playlist_callback(self, events):
        self.remove_widgets()
        self.playlists_page()

if __name__ == "__main__":
    SpotifyApp().run()