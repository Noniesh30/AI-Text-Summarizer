import streamlit as st
from langchain_groq import ChatGroq  # ✅ FIXED IMPORT
from langchain.schema import SystemMessage, HumanMessage
from PyPDF2 import PdfReader
from docx import Document
import os
from dotenv import load_dotenv


# ✅ Load environment variables from .env
load_dotenv()
groq_api_key = os.getenv("groq_api")

# 📄 Load & extract text
def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        pdf = PdfReader(uploaded_file)
        return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    return ""

# 🧠 LangChain + Groq summarizer
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

# 🌐 Streamlit UI
st.set_page_config(page_title="AI Note Summarizer", page_icon="📝")
st.title("📝 AI-Powered Note Summarizer")
st.write("Upload a note file or paste your note text. Get a smart summary instantly.")

uploaded_file = st.file_uploader("📎 Upload .txt, .pdf, or .docx", type=["txt", "pdf", "docx"])
note_input = st.text_area("✍️ Or paste your note here")

note_content = ""
if uploaded_file:
    note_content = extract_text_from_file(uploaded_file)
elif note_input:
    note_content = note_input

if note_content:
    if st.button("Summarize"):
        with st.spinner("Summarizing using Groq + LangChain..."):
            summary = summarize_text(note_content)
        st.subheader("📌 Summary:")
        st.write(summary)
