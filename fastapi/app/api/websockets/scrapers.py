from fastapi import WebSocket, Depends
from dataclasses import dataclass, asdict
from api.shared.ScraperHandler import ScraperHandler
from db.database import SessionLocal
from sqlalchemy.orm import Session


@dataclass
class request:
    action: str
    params: dict

    def to_dict(self):
        return asdict(self)


@dataclass
class response:
    status: str
    message: str

    def to_dict(self):
        return asdict(self)


def get_db():
    db = SessionLocal()

    try:
        yield db
    except:
        db.close()


async def websocket_scrapers(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    await websocket.send_json(response("ok", "connected to scraper websockect!").to_dict())

    scraper_handler = ScraperHandler(db)

    while True:
        try:
            data = await websocket.receive_json()
            await websocket.send_json(response("ok", "action recieved").to_dict())
        except:
            raise ConnectionError("Error while receiving data from scraper websocket")

        try:
            data = request(**data)
        except:
            await websocket.send_json(response("error", "invalid request").to_dict())
            continue
        try:
            if data.action == "start":
                handler_res = await scraper_handler.start_task(
                    data.params["targets"], data.params["id_number"]
                )
                await websocket.send_json(handler_res.model_dump(mode="json"))

                async for item in scraper_handler.run_observer(handler_res.id):
                    await websocket.send_json(item.model_dump(mode="json"))

                await websocket.send_json(response("ok", "finished").to_dict())
            elif data.action == "close":
                await websocket.send_json(response("ok", "closing connection").to_dict())
                await websocket.close()
                break
            else:
                await websocket.send_json(response("error", "invalid action").to_dict())
        except Exception as e:
            await websocket.send_json(
                response("error", f"error while processing action: {e}").to_dict()
            )
