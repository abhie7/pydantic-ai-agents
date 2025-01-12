from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from pydantic_ai import Agent

from lmstudio_model import LMStudioModel

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chatbot</title>
        <style>
            body {
                font-family: 'Geist Mono', sans-serif !important;
                background-color: #1C2536;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .chat-container {
                width: 800px;
                background: #303C4F;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                overflow: hidden;
            }
            .chat-header {
                background: #415062;
                color: #E0E3E0;
                padding: 10px;
                text-align: center;
            }
            .chat-messages {
                padding: 10px;
                height: 600px;
                overflow-y: auto;
                border-bottom: 1px solid #415062;
                color: #E0E3E0;
            }
            .chat-input {
                display: flex;
                padding: 10px;
            }
            .chat-input input {
                font-family: 'Geist Mono', sans-serif !important;
                flex: 1;
                padding: 10px;
                border: 1px solid #E0E3E0;
                border-radius: 4px;
                margin-right: 10px;
            }

            .chat-input input:focus {
                outline: none;
                focus: none;
            }

            .chat-input button {
                font-family: 'Geist Mono', sans-serif !important;
                padding: 10px 20px;
                border: none;
                background: #415062;
                color: #E0E3E0;
                border-radius: 4px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
          <div class="chat-container">
            <div class="chat-header">
                Chatbot
            </div>
            <div class="chat-messages" id="chat-messages">
                <!-- Messages will appear here -->
            </div>
            <div class="chat-input">
                <input type="text" id="message-input" placeholder="Type a message...">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
        <script>
            const ws = new WebSocket("ws://localhost:8000/ws");

            ws.onopen = function(event) {
                console.log("WebSocket is open now.");
            };

            ws.onmessage = function(event) {
                const messages = document.getElementById('chat-messages');
                const message = document.createElement('div');
                message.textContent = event.data;
                console.log(event.data);
                messages.appendChild(message);
            };

            function sendMessage() {
                const input = document.getElementById('message-input');
                const userMessage = input.value;

                // Display user message
                const messages = document.getElementById('chat-messages');
                const userMessageDiv = document.createElement('div');
                userMessageDiv.textContent = "You: " + userMessage;
                messages.appendChild(userMessageDiv);

                // Send user message to WebSocket
                ws.send(userMessage);
                input.value = '';
            }

            // Add event listener for Enter key
            document.getElementById('message-input').addEventListener('keydown', function(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get():
    return html

# agent = Agent(
#     model=LMStudioModel(base_url="http://localhost:8000"),
#     system_prompt="Be as fun as possible."
# )

# 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

agent = Agent(
    model="groq:llama-3.2-3b-preview",
    # api_key="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",
    system_prompt="Be as fun as possible."
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    async for data in websocket.iter_text():
        result = await agent.run(user_prompt=data, message_history=[])
        await websocket.send_text(result.data)