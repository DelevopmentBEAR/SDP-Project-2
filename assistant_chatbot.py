import os
from google import genai
from google.genai import types
import sys

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("Set the GEMINI_API_KEY environment variable first.")

client = genai.Client(api_key=api_key)

try:
    with open('chat_system_instruction.txt', 'r') as f:
        system_instruction_text = f.read()
except:
    print("Missing system instruction, quiting program")
    sys.exit()

while True:
    question = input("> ")
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction_text
        )
    )
    print(response.text)