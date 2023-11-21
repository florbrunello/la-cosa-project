from fastapi import FastAPI
from src.settings import DATABASE_FILENAME
from src.theThing.models.db import db
from src.theThing.games import endpoints as games_endpoints
from src.theThing.messages.endpoints import message_router
from fastapi.middleware.cors import CORSMiddleware
import socketio
from src.theThing.games.socket_handler import socketio_app

app = FastAPI()
app.include_router(games_endpoints.router)
app.include_router(message_router)
app.mount("/socket.io", socketio_app)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "La Cosa"}


# socketio_app = socketio.ASGIApp(sio, app)

db.bind(provider="sqlite", filename=DATABASE_FILENAME, create_db=True)
db.generate_mapping(create_tables=True)
