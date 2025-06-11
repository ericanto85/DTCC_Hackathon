
# --- Agent 1: Extract User Profile (e.g. Age, Risk Preference)
def extract_user_profile(text: str) -> dict:
    prompt = f"""
    You are a user profile extraction expert. From the input: "{text}", extract the following:
    - Age (approximate if not exact)
    - Risk tolerance (Low, Medium, High)
    Respond in JSON.
    """
    output = llm(prompt=prompt, stop=["\n\n"])
    print(output)
    return json.loads(output['choices'][0]['text'])

# --- Agent 2: Recommend Mutual Funds based on extracted profile + DB
def recommend_mutual_funds(profile: dict, fund_list: list) -> str:
    age = profile.get("Age", "unknown")
    risk = profile.get("Risk tolerance", "Medium")
    
    funds_text = "\n".join([
        f"- {fund['name']} ({fund['category']}, Risk: {fund['risk_score']})"
        for fund in fund_list
    ])

    prompt = f"""
    You are an expert financial advisor. The user's age is {age} and they have a {risk} risk tolerance.
    Here are some mutual fund options from the database:

    {funds_text}

    Suggest the most suitable 2-3 funds from this list with reasons.
    """
    output = llm(prompt=prompt, stop=["\n\n"])
    return output['choices'][0]['text']