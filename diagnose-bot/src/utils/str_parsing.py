def parse_str(json_str):
    return json_str.replace('\\"', "'").replace("```json",'').replace("```",'')

import re
import json

def parse_str(text: str) -> str:
    """
    Extracts and sanitizes JSON string from LLM output.
    Fixes common errors like:
    - Markdown fences (```json ... ```)
    - Unescaped quotes
    - Missing commas between JSON key/value pairs
    - Trailing commas
    """
    # 1. Extract only JSON-like content
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    # 2. Remove markdown fences if present
    text = re.sub(r"```(?:json)?", "", text).strip("` \n")
    text = text.replace('\\"', "'").replace("```json",'').replace("```",'')
    
    # 3. Fix unescaped quotes around keys
    text = re.sub(r"([,{]\s*)([a-zA-Z0-9_-]+)(\s*:\s*)", r'\1"\2"\3', text)

    # 4. Ensure commas between key-value pairs
    text = re.sub(r'"\s*}\s*"', '"}', text)   # avoid merging objects
    text = re.sub(r'}\s*{', '},{', text)      # missing commas between objects

    # 5. Remove trailing commas before } or ]
    text = re.sub(r",\s*([}\]])", r"\1", text)

    # 6. Escape stray backslashes
    text = text.replace("\\", "\\\\")

    # Validate or raise error with explanation
    try:
        json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse JSON after cleaning. Error: {e}\nText: {text}")

    return text
