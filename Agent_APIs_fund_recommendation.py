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
#openai.api_key =

# --- Database connection
DB_PARAMS = {
    'dbname': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_wxIXSUf28Gpt',
    'host': 'ep-square-night-a5rzba7h.us-east-2.aws.neon.tech',
    'port': 5432,
    'schema':'MF_Data'
}

class UserInput(BaseModel):
    question: str
    answer: str

class ListUserInput(BaseModel):
    items: list[UserInput]


def query_mutual_funds(goal_id: int):
    conn = psycopg2.connect(
        dbname=DB_PARAMS['dbname'],
        user=DB_PARAMS['user'],
        password=DB_PARAMS['password'],
        host=DB_PARAMS['host'],
        port=DB_PARAMS['port']
    )
    cur = conn.cursor()

    if 'schema' in DB_PARAMS:
        cur.execute(f"SET search_path TO {DB_PARAMS['schema']}")

    query = """ SELECT target_amount, target_date, phone_number FROM "MF_Data"."goal_details" WHERE goal_id = %s; """
    cur.execute(query,(goal_id,))
    goal = cur.fetchone()
    goal_target_amount = goal[0]
    goal_target_date = goal[1]
    phone_number = goal[2]

    query = """ SELECT risk FROM "MF_Data"."user_profile" WHERE phone_number = %s; """
    cur.execute(query,(phone_number,))
    profile_risk = cur.fetchone()
    risk = profile_risk[0]

    query = """ SELECT fund_name, nav,one_year_return,three_year_return FROM "MF_Data"."mf_fund_data" WHERE risk = %s; """
    cur.execute(query,(risk,))
    results = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "funds": [
            {
                'fund_name': row[0],
                'nav': row[1],
                'one_year_return': row[2],
                'three_year_return': row[3],
            } for row in results
        ],
        'goal_target_amount': goal_target_amount,
        'goal_target_date': goal_target_date,
        'risk': risk
    }


def recommend_mutual_funds(fund_list: list, goal_target_amount: int, goal_target_date: date, risk: int):
    funds_text = "\n".join([
        f"- {fund['fund_name']} (nav: {fund['nav']}) (one_year_return: {fund['one_year_return']}) (three_year_return: {fund['three_year_return']})"
        for fund in fund_list
    ])

    prompt = f"""
        You are an expert financial advisor. and the candidate have a {risk} risk tolerance based on the numerical value 1 being lowest risk and 5 being highest risk. 
        The candidate requires to reach the target of {goal_target_amount} before {goal_target_date}. 
        Here are some mutual fund options from the database:

        {funds_text}

        Suggest the most suitable 2-3 funds and the respective Systematic investment amount for each fund.
        Respond ONLY as a list of dictionaries.
        ["fund_name": name, "SIP": amount", "fund_name": name, "SIP": amount", "fund_name": name, "SIP": amount"]

        
        As the output is displayed in mobile UI, give only the fund name,
        dont give any other explanation.
        """
    response = openai.ChatCompletion.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    print(response.choices[0].message.content.strip())
    return json.loads(response.choices[0].message.content.strip())


class FundInput (BaseModel):
    goal_id: int
@app.post("/fund_recommendation")
async def fund_recommendation(fund_input: FundInput):
    goal_id = fund_input.goal_id
    fund_all = query_mutual_funds(goal_id)
    fund_list = fund_all['funds']
    goal_target_amount = fund_all['goal_target_amount']
    goal_target_date = fund_all['goal_target_date']
    risk = fund_all['risk']
    print(fund_list,goal_target_amount,goal_target_date,risk)
    recommendation = recommend_mutual_funds(fund_list,goal_target_amount,goal_target_date,risk)
    return {
        'goal_id': goal_id,
        'recommendation': recommendation

    }