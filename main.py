from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from database.client import messages, sessions
from bson import ObjectId

app = FastAPI()

allowed_origin = "http://localhost:1234"

app.add_middleware(CORSMiddleware, allow_origins=allowed_origin, allow_credentials=True)


@app.get("/")
async def get_messages(request: Request, response: Response):
    session = request.cookies.get("session")
    if not session:
        response.status_code = 401
        return {"error": "Unauthorized"}
    doesSessionExist = sessions.find_one({"_id": ObjectId(session)})
    if not doesSessionExist:
        return {"error": "Unauthorized"}
    messagesList = []
    # Get messages from mongo
    for message in messages.find():
        message["_id"] = str(message["_id"])
        messagesList.append(message)
    return {"messages": messagesList}


@app.post("/")
async def take_username(request: Request, response: Response):
    form = await request.form()
    username = form.get("username")
    if not username:
        response.status_code = 400
        return {"error": "Username is required"}
    doesUsernameExist = sessions.find_one({"username": username})
    if doesUsernameExist:
        response.status_code = 400
        return {"error": "Username already exists"}
    session = sessions.insert_one({"username": username})
    response.set_cookie("session", str(session.inserted_id))
    return {"session": str(session.inserted_id)}


@app.get("/me")
async def get_me(request: Request, response: Response):
    session = request.cookies.get("session")
    if not session:
        response.status_code = 401
        return {"error": "Unauthorized"}
    doesSessionExist = sessions.find_one({"_id": ObjectId(session)})
    if not doesSessionExist:
        response.status_code = 401
        return {"error": "Unauthorized"}
    return {"username": doesSessionExist["username"]}


# Damn really? U must manually keep track of all the connections?
websocket_connections: list[WebSocket] = []


@app.websocket("/chat")
async def chat_endpoint(websocket: WebSocket):
    session = websocket.cookies.get("session")
    if not session:
        await websocket.close()
        return
    doesSessionExist = sessions.find_one({"_id": ObjectId(session)})
    if not doesSessionExist:
        await websocket.close()
        return
    await websocket.accept()
    websocket_connections.append(websocket)
    while True:
        try:
            data = await websocket.receive_json()
        except WebSocketDisconnect:
            websocket_connections.remove(websocket)
            break
        if data["type"] == "message":
            message = data["message"] if data.get("message") else None
            if not message:
                continue
            username = doesSessionExist.get("username")
            if not username:
                continue
            user = sessions.find_one({"username": username})
            messages.insert_one({"message": message, "username": username})
            for connection in websocket_connections:
                await connection.send_json(
                    {"type": "message", "message": message, "username": username}
                )
    await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="", port=3000, reload=True)
