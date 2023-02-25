from oauth2_api_client import OAuth2ApiClient
import json
from spotify_endpoints import TeamsApiEndpoints

class TeamsClient(OAuth2ApiClient):
    
    def __init__(self):
        super().__init__("teams", TeamsApiEndpoints(), includeClientSecret= False)
    
    def getUsers(self):
        r = self.makeRequest(self._api.Users)
        data = json.loads(r.text)
        print(json.dumps(data, indent=2))

    def getMe(self):
        r = self.makeRequest(self._api.Me)
        data = json.loads(r.text)
        print(json.dumps(data, indent=2))
        if "id" in data:
            return data["id"]
        return None
    
    def getPresence(self):
        r = self.makeRequest(self._api.Presence)
        data = json.loads(r.text)
        print(json.dumps(data, indent=2))
    
    def setPresence(self, msg):
        r = self.makePostRequest(self._api.SetPresence, {
            "statusMessage": {
              "message": {
                  "content": msg,
                  "contentType": "text"
              }
            }
        })
        print(r.status_code)
        print(r.text)
        print(r.reason)
