from fastapi import APIRouter, WebSocket

router = APIRouter(prefix="/web_sockets")


@router.websocket("/scrappers")
async def ws_scrappers(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Connected")

    while True:
        data = await websocket.receive_json()
        await websocket.send_text(f"Message text was: {data}")

    await websocket.close()
