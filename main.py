
from config import CLIENT_ID, CLIENT_SECRET
from requests import post, get
import base64
import json
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from webbrowser import open
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image, AsyncImage
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

REDIRECT_URL = "https://www.google.com" # -> this worked? LOL
BASE_AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPE = [
        "user-read-email",
        "playlist-read-collaborative"
        ]

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
    
spotify = Spotify()

class SpotifyApp(App):
    authorization_data = ""
    profile_data = ""
    controls = []
    def build(self):
        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.7)
        self.window.pos_hint = {"center_x": 0.5, "center_y":0.5}

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

        return self.window
    
    def add_widgets(self):
        for elem in self.controls:
            self.window.add_widget(elem)

    def remove_widgets(self):
        for elem in self.controls:
            self.window.remove_widget(elem)

    def authorize_callback(self, event):
        spotify.authorize()

    def submit_callback(self, event):
        if self.redirect_url.text == "":
            print("Empty")
        else:
            self.authorization_data = spotify.fetching_token(self.redirect_url.text)
            self.profile_data = spotify.get_my_data()
            self.remove_widgets()
            self.controls = []
            self.main_page()

    def main_page(self):
        name = self.profile_data["display_name"]
        pfp_image_url = self.profile_data["images"][0]["url"]

        self.profile_picture = AsyncImage(
            source=pfp_image_url,
            )
        self.greeting = Label(
            text=f"Hello {name}!"
        )

        self.controls = [
            self.profile_picture,
            self.greeting
        ]
        self.add_widgets()

if __name__ == "__main__":
    SpotifyApp().run()