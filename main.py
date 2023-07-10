
from config import CLIENT_ID, CLIENT_SECRET
from requests import post, get, put
import base64
import json
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
import spotipy
from spotipy.oauth2 import SpotifyOAuth
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
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox

REDIRECT_URL = "https://www.google.com" # -> this worked? LOL
BASE_AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPE = [
        "user-read-email",
        "playlist-read-collaborative",
        "playlist-read-private",
        "user-modify-playback-state",
        "playlist-modify-public",
        "playlist-modify-private"
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
        # self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
        #                 client_secret=CLIENT_SECRET,
        #                 redirect_uri=REDIRECT_URL,
        #                 scope=SCOPE))
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

    def get_spotify_id(self,id):
        url = "https://api.spotify.com/v1/search"
        query = f"?q={id}&type=artist"

        query_url = url + query
        result = self.spotify.get(query_url, headers=self.headers)
        results = json.loads(result.content)
        results = self.search_in_spotify(id)
        return results["artists"]["items"][0]["id"]
    
    def search_in_spotify(self, keyword):
        url = "https://api.spotify.com/v1/search"
        types = ["album", "artist", "playlist", "track", "show", "episode", "audiobook"]
        result = get(
            url=url,
            headers=self.headers,
            params= {
                "q" : keyword,
                "type" : types
            })
        results = json.loads(result.content)
        return results
    
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
        url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        result = get(url, headers=self.headers)
        results = json.loads(result.content)

        return results
    
    def make_playlist(self, name_of_playlist, is_public):
        user_id = self.get_my_data()["id"]
        url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        result = put(url=url,headers=self.headers,data={
            "name" : name_of_playlist,
            "public" : is_public
        })
        return result
    
spotify = Spotify()

class SpotifyApp(MDApp):
    authorization_data = ""
    profile_data = ""
    controls = []
    playlist_ctrls = {}
    playlist_songs = {}
    default_image = "https://img.freepik.com/free-icon/user_318-644325.jpg"
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
            multiline=True,
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

    def go_to_start_page(self,event):
        self.remove_widgets()
        self.on_start()
    
    def main_page(self):
        name = self.profile_data["display_name"]
        pfp_image_url = self.default_image if len(self.profile_data["images"]) == 0 else self.profile_data["images"][0]["url"]

        self.search_bar = TextInput(
            hint_text="Search",
            multiline=False,
            size_hint=(0.5,0.5))
        
        self.search_button = Button(
            text="Search",
            size_hint=(0.3,0.5),
            background_color ='#47B5FF'
        )
        self.search_button.bind(on_press=self.searching)

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

        self.logout_btn = Button(
            text="Logout",
            size_hint= (1,0.5),
            bold= True,
            background_color ='#47B5FF',
        )
        self.logout_btn.bind(on_press=self.go_to_start_page)

        self.controls = [
            self.search_bar,
            self.search_button,
            self.profile_picture,
            self.greeting,
            self.playlists_btn,
            self.logout_btn
        ]
        self.add_widgets()

    def search_page(self, searched, data):
        title = Label(text=searched, size_hint=(0.2, 0.1))
        to_be_added_to_controls = MDScrollView()
        md_list = MDList()
        to_be_added_to_controls.add_widget(md_list)

        for item in data["albums"]["items"]: 
            image = self.default_image if len(item["images"]) == 0 else item["images"][0]["url"]
            name = item["name"]
            url = item["external_urls"]["spotify"]

            output = OneLineAvatarListItem(ImageLeftWidget(source=image), text=name, theme_text_color="Custom", text_color=(1, 1, 1, 1),on_release=self.go_to_play_playlist_song)
            self.playlist_songs[output] = url
            md_list.add_widget(output)

        self.controls.append(title)
        self.controls.append(to_be_added_to_controls)
        self.controls.append(Button(text="Back", on_press=self.go_to_main_page, size_hint=(0.2, 0.1)))
        self.add_widgets()

    def searching(self, event):
        if self.search_bar.text != "":
            search_data = spotify.search_in_spotify(self.search_bar.text)
            self.remove_widgets()
            self.search_page(self.search_bar.text, search_data)
        else:
            self.show_error_popup("Empty Search Bar")

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
            image = self.default_image if len(track["track"]["album"]["images"]) == 0 else track["track"]["album"]["images"][0]["url"]
            item = OneLineAvatarListItem(ImageLeftWidget(source=image), text=track["track"]["name"], theme_text_color="Custom", text_color=(1, 1, 1, 1),on_release=self.go_to_play_playlist_song)
            self.playlist_songs[item] = track["track"]["external_urls"]["spotify"]
            md_list.add_widget(item)
        self.controls.append(Label(text=name, size_hint=(0.1,0.1)))
        self.controls.append(to_be_added_to_controls)
        self.controls.append(Button(text="Back", on_press=self.playlist_callback, size_hint=(0.2, 0.1)))
        self.add_widgets()

    '''
    turns out that in order to play a song, you have to use spotipy since the method im using for this is weird
    which, in turn, will make me have to change the entire code around and i am NOT doing that, so until i feel
    like implementing it and changing the code, this feature will unforunately not be fully implemented.
    '''

    def go_to_play_playlist_song(self, event):
        url_of_song = self.playlist_songs[event]
        open(url_of_song)

    def playlists_page(self):
        playlist_data = spotify.get_user_playlists()
        all_playlists = playlist_data["items"]

        to_be_added_to_controls = MDScrollView()
        md_list = MDList()
        to_be_added_to_controls.add_widget(md_list)

        for playlist in all_playlists:
            image = self.default_image if len(playlist["images"]) == 0 else playlist["images"][0]["url"]
            item = OneLineAvatarListItem(
                    ImageLeftWidget(source=image),
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1), 
                    text=playlist["name"],
                    on_release = self.indiv_playlist
                )
            self.playlist_ctrls[item] = playlist
            md_list.add_widget(item)

        self.controls.append(to_be_added_to_controls)
        self.controls.append(Button(text="Make Playlist", size_hint=(0.2, 0.1), on_press=self.go_to_make_playlist))
        self.controls.append(Button(text="Back", on_press=self.go_to_main_page, size_hint=(0.2, 0.1)))
        self.add_widgets()

    def make_playlist(self, event):
        print(self.publicity.active)
        if self.get_name.text != "":
            def close_pop(event):
                popup.dismiss()
                self.remove_widgets()
                self.playlists_page()
            spotify.make_playlist(self.get_name.text, self.publicity.active)
            content_for_popup = Button(text="Close")
            popup = Popup(title="Playlist Created!", content=content_for_popup, size_hint=(0.2,0.2))
            content_for_popup.bind(on_press=close_pop)
            popup.open()
        else:
            self.show_error_popup("Empty Name")

    def make_playlist_page(self):
        self.get_name = TextInput(
            hint_text = "Name of Playlist",
            size_hint=(0.2, 0.1)
        )

        self.publicity = CheckBox(
        ) #disabled

        self.make_playlist_button = Button(
            text="Create playlist",
            on_press = self.make_playlist,
            size_hint=(0.2, 0.1)
        )

        self.controls.append(self.get_name)
        self.controls.append(Label(text="Make public", size_hint=(0.2, 0.1)))
        self.controls.append(self.publicity)
        self.controls.append(self.make_playlist_button)
        self.add_widgets()

    def go_to_make_playlist(self, event):
        self.remove_widgets()
        self.make_playlist_page()
    
    def add_widgets(self):
        for elem in self.controls:
            self.window.add_widget(elem)

    def remove_widgets(self):
        for elem in self.controls:
            self.window.remove_widget(elem)
        self.controls = []

    def authorize_callback(self, event):
        spotify.authorize()

    def show_error_popup(self, text):
        def close_pop(event):
            popup.dismiss()
            
        content_for_popup = Button(text="Close")
        popup = Popup(title=text, content=content_for_popup, size_hint=(0.2,0.2))
        content_for_popup.bind(on_press=close_pop)
        popup.open()

    def submit_callback(self, event):
        if self.redirect_url.text == "":
            self.show_error_popup("Empty URL")
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