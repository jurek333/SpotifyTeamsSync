from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

class PyLocalServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        u = urlparse(self.path)
        params = parse_qs(u.query)
        if "code" in params:
            self.server.setCode(params["code"][0])
        if "state" in params:
            self.server.setState(params["state"][0])

        error = None
        errorDescription = ""
        if "error" in params:
            error = params["error"]
        if error == None or error == "" or error == []:
            self.GotCode = True
        else:
            self.GotCode = False
        if "error_description" in params:
            errorDescription = params["error_description"]

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>SpotifyTeamsSync Authentication</title></head>", "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        if error != "":
            self.wfile.write(bytes(f"<p>Error: {error}</p><p>{errorDescription}</p>", "utf-8"))    
        self.wfile.write(bytes("<p>This browser/tab maybe closed.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

class PyLocalServer(HTTPServer):
    code = ''
    gotCode = False
    _hostName = "localhost"
    _serverPort = 8443
    _redirectUrl = f"http://{_hostName}:{_serverPort}/callback"

    def __init__(self, handlerClass = PyLocalServerHandler):
        super().__init__((self._hostName, self._serverPort), handlerClass)

    def getRedirectUrl(self):
        return self._redirectUrl

    def setCode(self, value):
        self.code = value
        self.gotCode = True

    def getCode(self) -> str:
        return self.code
    
    def hasCode(self) -> bool:
        return self.gotCode

    def setState(self, value: str):
        self.state = value
    
    def getState(self) -> str:
        return self.state
        
def runServer(srv):
    try:
        srv.handle_request()
    except KeyboardInterrupt:
        pass
        
    srv.server_close()