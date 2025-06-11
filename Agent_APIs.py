import re
import psycopg2
import json
import openai
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
from datetime import date

app = FastAPI()

# --- OpenAI API Key (use environment variable or hardcoded)
openai.api_key = 



class UserInput(BaseModel):
    question: str
    answer: str

class ListUserInput(BaseModel):
    items: list[UserInput]

# --- Agent 1: calculate risk
@app.post("/calculate_risk")
async def calculate_risk(risk_input: ListUserInput):
    print(risk_input.items[0].question)
    print(len(risk_input.items))
    prompt = f"""
        You are a financial advisor assistant. Based on the user's answers to a few questions, determine their investment risk profile as one of the following: **Low**, **Medium**, or **High**.

    Respond only with a JSON object in the following format:
    {{
      "risk_rating": "Low | Medium | High",
      "reason": "..."
    }} 
    Questions and Answers:
    1.  Q: "{risk_input.items[0].question}"
        A: "{risk_input.items[0].answer}"
    2.  Q: "{risk_input.items[1].question}"
        A: "{risk_input.items[1].answer}"
    3.  Q: "{risk_input.items[2].question}"
        A: "{risk_input.items[2].answer}"
    4.  Q: "{risk_input.items[3].question}"
        A: "{risk_input.items[3].answer}"
    5.  Q: "{risk_input.items[4].question}"
        A: "{risk_input.items[4].answer}"
    Based on this, give your JSON response.
        """
    response = openai.ChatCompletion.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    output = response.choices[0].message.content.strip()
    print("Extracted profile:", output)
    return json.loads(output)
