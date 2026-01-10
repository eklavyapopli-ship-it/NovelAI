from google import genai
from pydantic import BaseModel, Field
from typing import Union
from dotenv import load_dotenv
load_dotenv()
class Novel(BaseModel):
    BookName: str = Field(description="Name of the Novel")
    AIopinion: str = Field(description="AI opinion / reply based on the user query strictly in accordance to novel")

class Reply(BaseModel):
    AIopinion: str = Field(description="AI opinion / reply based on the user query strictly in accordance to novel")
class ModerationResult(BaseModel):
    decision: Union[Novel, Reply]

client = genai.Client()

def process(query: str):
    systemPrompt = f'''
You are Libris, an insightful literary companion AI. You discuss novels, themes, and characters with depth, offering thoughtful interpretations, emotional insights, and reflective questions. Never quote books directly; focus on analysis, opinions, and engaging conversation. Adapt your tone to be cozy, dark, or philosophical depending on the user’s mood.
'''
    response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=query,
    config={
        "response_mime_type": "application/json",
        "response_json_schema": Novel.model_json_schema(),
        "system_instruction":systemPrompt
    },
)
    result = Novel.model_validate_json(response.text)
    return result.AIopinion
    