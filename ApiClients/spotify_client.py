import json
from oauth2_api_client import OAuth2ApiClient

from song import Song
from spotify_endpoints import SpotifyEndpoints

class SpotifyClient(OAuth2ApiClient):

    def __init__(self):
        super().__init__("spotify", SpotifyEndpoints(), includeClientSecret= True)

    def getSong(self) -> Song:
        r = self.makeRequest(self._api.PlayingTrack)
        if r.status_code == 200:
            data = json.loads(r.text)
            artists = ", ".join([art["name"] for art in data["item"]["artists"]])
            return Song(data["item"]["name"], artists)
        return None