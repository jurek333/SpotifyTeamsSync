import requests
import json
import base64
import uuid
from ApiClients.local_server import PyLocalServer, runServer
import urllib.parse
import threading
from datetime import datetime, timedelta
from time import sleep
from webbrowser import open_new
from spotify_endpoints import OAuth2ApiEndpoints

def runBrowser(url):
    sleep(1)
    open_new(url)

class OAuth2ApiClient:
    _authData = {}

    def __init__(self, appName, endpoints: OAuth2ApiEndpoints, includeClientSecret: bool = False):
        self._includeClientSecret = includeClientSecret
        self._appName = appName
        self._cacheFilePath = appName + ".cache.json"
        self._configFilePath = appName + ".config.json"
        self._token = None
        self._expiredAt = datetime.now()
        self._timeoutTask = None
        self._loadConfig()
        self._loadCache()
        self.setApiEndpoints(endpoints)

    def setApiEndpoints(self, endpoints: OAuth2ApiEndpoints):
        self._api = endpoints
    
    def _consumeOAuthRespone(self, response):
        data = json.loads(response.text)
        self._authData = data
        self._expiredAt = datetime.now() + timedelta(0, data["expires_in"])
        self._authData["expiresAt"] = str(self._expiredAt)
        self._token = {"Authorization": data["token_type"]+" "+ data["access_token"]}
        self._saveCache()
    
    def _saveCache(self):
        with open(self._cacheFilePath, "w") as cacheFile:
            cacheFile.write(json.dumps(self._authData, indent=2))
    
    def _loadCache(self):
        with open(self._cacheFilePath, "r") as cacheFile:
            content = cacheFile.read()
            if content == "":
                return
            self._authData = json.loads(content)
            if "token_type" in self._authData and "access_token" in self._authData:
                self._token = {"Authorization": self._authData["token_type"]+" "+ self._authData["access_token"]}
            if "expiresAt" in self._authData:
                self._expiredAt = datetime.fromisoformat(self._authData["expiresAt"])

    def _loadConfig(self):
        config = None
        with open(self._configFilePath, "r") as configFile:
            config = json.loads(configFile.read())
        if None == config:
            print("Cannot read spotfy configuration")
            exit(1)
        self._client_id = config["client_id"]
        self._client_seret = config["client_secret"]
        if "tenant" in config:
            self._tenant = config["tenant"]
    
    def _hasToken(self):
        if self._authData is None:
            return False
        if self._token == None or self._token == "":
            return False
        if self._expiredAt < datetime.now():
            return False
        return True
    
    
    def _runBrowser(self, state, redirectUrl):
        oAuthParams = {
            "client_id": self._client_id,
            "response_type": "code",
            "redirect_uri": redirectUrl,
            "state": state,
            "scope": self._api.Scopes
        }
        taskBrowser = threading.Thread(target=runBrowser, args=[self._api.Authorize +"?"+ urllib.parse.urlencode(oAuthParams)])
        taskBrowser.start()
        taskBrowser.join()

    def _refreshToken(self):
        tokenParams = {
            "grant_type": "refresh_token",
            "refresh_token": self._authData["refreshToken"]
        }
        tokenHeader = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic "+base64.b64encode(bytes(f"{self._client_id}:{self._client_seret}",'utf-8')).decode('utf-8')
        }
        rt = requests.post(self._api.OAuthToken, data=tokenParams, headers=tokenHeader)
        if rt.status_code == 200:
            self._consumeOAuthRespone(rt)
            return True

        return False        

    def _getToken(self):
        if self._expiredAt < datetime.now() and "token_refresh" in self._authData:
            print("-- try to refresh token")
            if self._refreshToken():
                print("-- token was refreshed")
                return True
        print("-- get new token")
        
        state = str(uuid.uuid4())
        srv = PyLocalServer()
        self._taskServer = threading.Thread(target=runServer, args=[srv])
        self._taskServer.start()

        self._runBrowser(state, srv.getRedirectUrl())
        
        self._taskServer.join()

        if not srv.hasCode():
            print(f"-- doesn't get code")
            return False
        self._code = srv.getCode() 
        print(f"-- got code: {self._code}")
        if srv.getState().strip() != state.strip():
            print(f"Received state doesn't match {srv.getState()} vs {state}. MitM situation?")
            return False

        tokenParams = {
            "scope": self._api.Scopes,
            "grant_type": "authorization_code",
            "code": self._code,
            "redirect_uri": srv.getRedirectUrl(),
            "client_id": self._client_id
        }
        tokenHeader = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        if self._includeClientSecret:
            tokenHeader["Authorization"] = "Basic "+base64.b64encode(bytes(f"{self._client_id}:{self._client_seret}",'utf-8')).decode('utf-8')

        rt = requests.post(self._api.OAuthToken, data=tokenParams, headers=tokenHeader)
        print(rt.status_code)
        print(rt.text)
        print(rt.reason)
        if rt.status_code == 200:
            self._consumeOAuthRespone(rt)
            return True

        return False
    
    def makePostRequest(self, endpoint, jsonObj):
        tryCount = 0
        while tryCount < 3:
            tryCount = tryCount + 1
            if not self._hasToken():
                if not self._getToken():
                    print(f"Cannot authenticate in {self._appName} service")
                    exit(1)
            else:
                print("-- use current token")
            print(f"request POST {endpoint}, json {json.dumps(jsonObj, indent=2)}")
            r = requests.post(endpoint, headers=self._token, json=jsonObj)
            if r.ok:
                return r
            elif r.status_code == 401:
                self._token = None
            else:
                return r
    
    def makeRequest(self, endpoint):
        tryCount = 0
        while tryCount < 3:
            tryCount = tryCount + 1
            if not self._hasToken():
                if not self._getToken():
                    print(f"Cannot authenticate in {self._appName} service")
                    exit(1)
            else:
                print("-- use current token")
            print(f"request GET {endpoint}")
            r = requests.get(endpoint, headers=self._token)
            if r.ok:
                return r
            elif r.status_code == 401:
                self._token = None
            else:
                return r