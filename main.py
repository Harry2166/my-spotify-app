
from config import CLIENT_ID, CLIENT_SECRET
from requests import post, get
import base64
import json
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from webbrowser import open

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

        redirect_response = input('Paste the full redirect URL here: ')
        auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)

        token = self.spotify.fetch_token(TOKEN_URL, auth=auth,
                authorization_response=redirect_response)
    
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
spotify.authorize()
print(spotify.get_my_data())
print(spotify.get_artist("Michael Jackson"))