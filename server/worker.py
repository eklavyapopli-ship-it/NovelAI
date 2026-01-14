from google import genai
from pydantic import BaseModel, Field
from openai import OpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from typing import Union
import json
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.mongodb import MongoDBSaver
load_dotenv()
class State(TypedDict):
    messages: Annotated[list, add_messages]
llm  = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    
)

systemPrompt = '''
You are Libris, an insightful literary companion AI. You discuss novels, themes, and characters with depth, offering thoughtful interpretations, emotional insights, and reflective questions. Never quote books directly; focus on analysis, opinions, and engaging conversation. Adapt your tone to be cozy, dark, or philosophical depending on the user’s mood.
Always respond in valid JSON format: {"response": "your reply here"}.
'''

def chatbot(state:State):
    response = llm.invoke(state.get("messages"))
    return {"messages":[response]}
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot",chatbot)
graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

def compile_graph_with_checkpointer(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)




def process(query:str):
    
    initial_state = {
    "messages": [
        SystemMessage(content=systemPrompt),
        HumanMessage(content=query)
    ]
}
    DB_URI = "mongodb://admin:admin@localhost:27017"
    with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
        graph_with_checkpointer = compile_graph_with_checkpointer(checkpointer=checkpointer)
        config = {
        "configurable":{
            "thread_id":"khush"
        }
    }    
        for chunk in graph_with_checkpointer.stream(State(initial_state),config, stream_mode="values"):
            last_msg = chunk["messages"][-1]
            if last_msg.type == "ai":
                return last_msg.content
