
class OAuth2ApiEndpoints:
    Scopes = ""
    Authorize = "http://localhost/authorize"
    OAuthToken = "http://localhost/api/token"


class TeamsApiEndpoints(OAuth2ApiEndpoints):
    Scopes = "https://graph.microsoft.com/.default"
    ApiUrl = "https://graph.microsoft.com/beta"
    Me = ApiUrl + "/me"
    Users = ApiUrl + "/users"
    Presence = ApiUrl + "/users/<userId>/presence"
    SetPresence = ApiUrl + "/users/<userId>/presence/setStatusMessage"
    Authorize =  "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    OAuthToken = "https://login.microsoftonline.com/common/oauth2/v2.0/token"


class SpotifyEndpoints(OAuth2ApiEndpoints):
    Scopes = "user-read-playback-state"
    ApiUrl = "https://api.spotify.com/v1"
    Authorize = "https://accounts.spotify.com/authorize"
    OAuthToken = "https://accounts.spotify.com/api/token"

    def __init__(self):
        self.Me = self.ApiUrl + "/me"
        self.Player = self.ApiUrl + "/me/player"
        self.PlayingTrack = self.ApiUrl + "/me/player/currently-playing"
