from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.sockets import ws_router

app = FastAPI()
app.include_router(ws_router)

origins = [
    "http://localhost:8088",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8088, reload=True)
