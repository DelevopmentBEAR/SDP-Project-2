import os
from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_INSTRUCTION_PATH = os.path.join(BASE_DIR, "chat_system_instruction.txt")
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def load_system_instruction():
    try:
        with open(SYSTEM_INSTRUCTION_PATH, "r", encoding="utf-8") as file:
            text = file.read().strip()
        return text or "You are a supportive writing coach helping authors overcome writer's block."
    except FileNotFoundError:
        return "You are a supportive writing coach helping authors overcome writer's block."


SYSTEM_INSTRUCTION = load_system_instruction()


def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your environment before starting the app."
        )
    return genai.Client(api_key=api_key)


def build_conversation_context(history):
    if not history:
        return ""

    context_lines = []
    for item in history[-8:]:
        role = (item.get("role") or "user").title()
        content = (item.get("content") or "").strip()
        if content:
            context_lines.append(f"{role}: {content}")
    return "\n\n".join(context_lines) + "\n\n"


def generate_response(message, history):
    client = get_client()
    context = build_conversation_context(history)
    prompt = f"{context}User: {message}"

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.7,
            max_output_tokens=600,
        ),
    )

    text = getattr(response, "text", "")
    if not text:
        return "I’m here to help. Try giving me a bit more about your story idea, where you’re stuck, or what the scene is supposed to do."
    return text.strip()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not message:
        return jsonify({"error": "Please enter a message first."}), 400

    try:
        reply = generate_response(message, history)
        return jsonify({"reply": reply})
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        app.logger.exception("LLM request failed")
        return jsonify({"error": "The writing coach is temporarily unavailable. Please try again in a moment."}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
