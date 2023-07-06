
from config import CLIENT_ID, CLIENT_SECRET
from requests import post, get
import base64
import json
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth

REDIRECT_URL = "https://www.google.com" # -> this worked? LOL
BASE_AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"

def get_token():
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

universal_token = get_token()

def get_auth_header():
    return {"Authorization":f"Bearer {universal_token}"}

def get_spotify_id(id,limit=1):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header()
    query = f"?q={id}&type=artist&limit={limit}"

    query_url = url + query
    result = get(query_url, headers=headers)
    results = json.loads(result.content)  
    return results["artists"]["items"][0]["id"]

def get_artist(artist):
    headers = get_auth_header()
    artist_id = get_spotify_id(artist)
    url = f"https://api.spotify.com/v1/artists/{artist_id}"

    result = get(url, headers=headers)
    results = json.loads(result.content)
    return results

def get_my_data():
    headers = get_auth_header()
    result = get("https://api.spotify.com/v1/me", headers=headers)
    results = json.loads(result.content)

    return results

### Spotify OAuth 2

scope = [
    "user-read-email",
    "playlist-read-collaborative"
]

spotify = OAuth2Session(CLIENT_ID, scope=scope, redirect_uri=REDIRECT_URL)

authorization_url, state = spotify.authorization_url(BASE_AUTH_URL)
print('Please go here and authorize: ', authorization_url)

# Get the authorization verifier code from the callback url
redirect_response = input('\n\nPaste the full redirect URL here: ')

auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)

# Fetch the access token
token = spotify.fetch_token(TOKEN_URL, auth=auth,
        authorization_response=redirect_response)

print(token)

# Fetch a protected resource, i.e. user profile
r = spotify.get('https://api.spotify.com/v1/me')
print(r.content)