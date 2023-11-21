from robyn import Robyn

from app.sockets import web_sockets

app = Robyn(__file__)
app.include_router(web_sockets)

if __name__ == "__main__":
    app.start(host='0.0.0.0', port='8088')
