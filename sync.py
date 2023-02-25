from ApiClients.spotify_client import SpotifyClient
from ApiClients.teams_client import TeamsClient

sc = SpotifyClient()
song = sc.getSong()
if song is not None:
    print(f"song: {song.Name} by {song.Artist}")

tm = TeamsClient()
tm.getMe()
tm.getPresence()
