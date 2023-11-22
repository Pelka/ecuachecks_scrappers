from robyn import Robyn, ALLOW_CORS
from robyn.authentication import BearerGetter
from app.auth import BasicAuthHandler
from app.sockets import web_sockets

app = Robyn(__file__)
app.include_router(web_sockets)

ALLOW_CORS(app, ["*"])

if __name__ == "__main__":
    app.start(host='0.0.0.0', port='8088')
