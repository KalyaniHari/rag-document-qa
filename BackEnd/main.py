from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from llm_service import get_llm_response, get_weather, get_tool_response
import json
# To install: pip install tavily-python


app = FastAPI(title="AI Knowledge Assistant Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = Field(default_factory=list)


@app.get("/")
def health():
    return {"message": "AI Knowledge Assistant backend is running."}


@app.post("/chat")
def chat(request: ChatRequest):
    history = [msg.model_dump() for msg in request.history]
    response = get_llm_response(request.message, history)
    finish_reason = response.choices[0].finish_reason
    reply = "place_holder"

    if finish_reason == "stop":
        reply = response.choices[0].message.content
    elif finish_reason == "tool_calls":
        tool_calls=response.choices[0].message.tool_calls
        tool_name=tool_calls[0].function.name
        tool_id=tool_calls[0].id
        tool_arguments=tool_calls[0].function.arguments

        try:
            tool_arguments = json.loads(tool_arguments)
            date=tool_arguments["Date"]
            city=tool_arguments["city"]
            if tool_name == "get_weather":
                weather=get_weather(date, city)
            
                response2=get_tool_response(request.message, response, tool_id, weather)
                reply=response2.choices[0].message.content

        except Exception as e:
            print(e)
            print("model gave invalid tool")

    return {"reply": reply}