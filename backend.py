from flask import Flask, request, jsonify, session
from flask_cors import CORS
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
from PyPDF2 import PdfReader
from docx import Document
import os
import json
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
CORS(app, supports_credentials=True)

load_dotenv()
groq_api_key = os.getenv("groq_api")

USERS = {
    "user1": "password123",
    "admin": "adminpass"
}

DATA_FILE = "summarized_data.json"

def extract_text(file_stream, file_type):
    if file_type == "application/pdf":
        pdf = PdfReader(file_stream)
        return "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file_stream)
        return "\n".join([p.text for p in doc.paragraphs])
    elif file_type == "text/plain":
        return file_stream.read().decode("utf-8")
    return ""

def summarize_text(text):
    chat = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama3-8b-8192"
    )
    messages = [
        SystemMessage(content="You are an assistant that summarizes academic and professional notes clearly."),
        HumanMessage(content=f"Summarize the following note:\n\n{text}")
    ]
    response = chat(messages)
    return response.content

def save_summary(user, text, summary):
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    if user not in data:
        data[user] = []

    data[user].append({"text": text, "summary": summary})

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/api/login", methods=["POST"])
def login():
    credentials = request.json
    username = credentials.get("username")
    password = credentials.get("password")
    if username in USERS and USERS[username] == password:
        session["username"] = username
        return jsonify({"message": "Login successful", "username": username})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return jsonify({"message": "Logged out"})

@app.route("/api/summarize", methods=["POST"])
def summarize():
    user = session.get("username")
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    text = data.get("text")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    summary = summarize_text(text)
    save_summary(user, text, summary)
    return jsonify({"summary": summary})

@app.route("/api/summarize-file", methods=["POST"])
def summarize_file():
    user = session.get("username")
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
    text = extract_text(file.stream, file.content_type)
    if not text:
        return jsonify({"error": "Unable to extract text"}), 400
    summary = summarize_text(text)
    save_summary(user, text, summary)
    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(debug=True)
