import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from tavily import TavilyClient

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)

api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

print("ENV FILE:", ENV_PATH)
print("API KEY FOUND:", "YES" if api_key else "NO")
print("KEY PREFIX:", api_key[:15] if api_key else "NONE")

SYSTEM_PROMPT = (
    "You are a helpful AI Knowledge Assistant. "
    "Answer user questions in a clear, structured, beginner-friendly way. "
    "Use short sections, bullet points, and simple language. "
    "Avoid long paragraphs. "
    "When explaining concepts, use this format when possible: "
    "1. Short answer "
    "2. Key points "
    "3. Simple example "
    "4. Final summary. "
    "Maintain conversation context across the chat. "
    "If you do not know something, say so instead of making up information. "
    "In the future, you will be connected to a RAG system for document-based answers."
)

#tools

tools = [
    { "type" : "function",
        "function": {
                      "name": "get_weather",
                      "description":"Tell weather on a given date in Delhi",
                      "parameters": {
                        "type": "object",
                        "properties": {
                            "Date":{
                                "type": "string",
                                "description" : "the date for which you need the weather should be in mm-dd-yy format"
                            },
                            "city":{
                                "type":"string",
                                "description":"tell the city for which you need the weather"
                            }
                        },
                        "required": ["Date","city"]
                            
                      }
        }
    }
]

tavily_client = TavilyClient(api_key=tavily_api_key)

client = OpenAI(api_key=api_key)

def get_llm_response(message: str, history: list) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": message},
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            tools=tools,
        )

        
        return response

    except OpenAIError as e:
        return f"Error: Unable to get a response from the AI service. ({e})"

    except Exception as e:
        return f"Error: An unexpected error occurred. ({e})"

def get_tool_response(user_message, llm_response, tool_call_id, tool_call_response):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
        llm_response.choices[0].message,
        {"role": "tool", "content": tool_call_response, "tool_call_id": tool_call_id }
]
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            tools=tools,
        )
        
        return response

    except OpenAIError as e:
        return f"Error: Unable to get a response from the AI service. ({e})"

    except Exception as e:
        return f"Error: An unexpected error occurred. ({e})"

def get_weather(date, city):
    response = tavily_client.search(
    query=f"weather in {city} on {date}?",
    include_answer="basic",
    search_depth="advanced")
    print(response["answer"])
    return response["answer"]




