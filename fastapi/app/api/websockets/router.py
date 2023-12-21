from fastapi import APIRouter
from api.websockets.scrapers import websocket_scrapers

Router = APIRouter(prefix="/websockets")
Router.add_api_websocket_route("/scrapers", websocket_scrapers)
