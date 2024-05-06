from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from preprocess import preprocess_data
import uvicorn
from pydantic import BaseModel
from llm import get_llm_response

app = FastAPI()

class ChatResponse(BaseModel):
    sender: str
    message: str

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form id="urlForm" onsubmit="setUrl(event)">
            <input type="text" id="urlInput" placeholder="Enter website URL" autocomplete="off"/>
            <button type="submit">Set URL</button>
        </form>
        <br><br>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8015/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var data = JSON.parse(event.data)
                var content = document.createTextNode(data.message)
                message.appendChild(content)
                messages.appendChild(message)
            };

            function setUrl(event) {
                event.preventDefault();
                alert("Please wait few seconds to load the website....")
                var urlInput = document.getElementById("urlInput").value;
                var data = { "url": urlInput };
                fetch("/set_url", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    if (data.success) {
                        alert("Website loaded successfully!!!");
                    }
                })
                .catch(error => console.error("Error:", error));
            }

            function sendMessage(event) {
                event.preventDefault();
                if (document.getElementById("urlInput").value === "") {
                    alert("Please enter a website url")
                }
                var messageInput = document.getElementById("messageText").value;
                ws.send(messageInput);
                document.getElementById("messageText").value = '';
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.post("/set_url")
async def set_url(request: Request):
    global db
    data = await request.json()
    url = data["url"]
    # Call your setUrl function here with the received URL
    print("Received URL:", url)
    result = preprocess_data(url)
    if result["success"]:
        print("DB created")
        db = result["db"]
        return {"success":True, "message": "URL received successfully"}
    else:
        print("DB not created")
        return {"success":False, "message": "Something went wrong!"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    chat_history = []
    while True:
        try:
            data = await websocket.receive_text()
            resp = ChatResponse(sender="user", message=data)
            resp.sender = "user"
            await websocket.send_json(resp.dict())

            llm_out = get_llm_response(data, db)
            result_response = ChatResponse(sender="bot", message=llm_out)
            result_response.sender = "bot"
            await websocket.send_json(result_response.dict())
        except WebSocketDisconnect:
            break
        except Exception as e:
            print(e)
            resp = ChatResponse(
                sender="bot",
                
                message="Sorry, something went wrong. Try again.",
            )
            resp.sender = "bot"
            await websocket.send_json(resp.dict())


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8015)
