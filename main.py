
from config import CLIENT_ID, CLIENT_SECRET
from requests import post, get
import base64
import json

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

