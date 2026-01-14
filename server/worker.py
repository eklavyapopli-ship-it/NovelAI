from google import genai
from pydantic import BaseModel, Field
from openai import OpenAI
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import Union
import json
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
load_dotenv()
class State(TypedDict):
    messages: Annotated[list, add_messages]

client = OpenAI(
    api_key= os.getenv('GOOGLE_API_KEY'),
    base_url= "https://generativelanguage.googleapis.com/v1beta/openai/"
)


systemPrompt = '''
You are Libris, an insightful literary companion AI. You discuss novels, themes, and characters with depth, offering thoughtful interpretations, emotional insights, and reflective questions. Never quote books directly; focus on analysis, opinions, and engaging conversation. Adapt your tone to be cozy, dark, or philosophical depending on the user’s mood.
Always respond in valid JSON format: {"response": "your reply here"}.
'''



def process(query: str):
    message = [ {"role":"system", "content": systemPrompt} ,{"role":"user","content":query} ]
    
    
    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        response_format={
        "type": "json_object"
    },
        temperature=0,
        messages=message
        
    )
    raw_content = response.choices[0].message.content
    parsed_response = json.loads(raw_content)
    return parsed_response["response"]



