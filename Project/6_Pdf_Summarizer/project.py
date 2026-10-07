import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader
import os

load_dotenv()

client = OpenAI()

st.set_page_config(
    page_title="Ejobindia PDF Reader",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Ejobindia PDF Reader Agent")
st.caption("Upload a PDF and ask questions about its content.")

st.divider()

# ---------------- CHAT HISTORY ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- PDF UPLOAD ----------------

uploaded_file = st.file_uploader(
    "📕 Upload PDF",
    type=["pdf"]
)

if uploaded_file is not None:

    reader = PdfReader(uploaded_file)

    pdfContent = ""

    for page in reader.pages:
        pdfContent += page.extract_text() or ""

    st.success("PDF uploaded successfully ✅")

    st.divider()

    # ---------------- SHOW CHAT HISTORY ----------------

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.write(message["content"])

    # ---------------- USER QUESTION ----------------

    user_prompt = st.chat_input(
        "Ask something about the PDF..."
    )

    if user_prompt:

        # Save user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_prompt
        })

        # Show user message
        with st.chat_message("user"):
            st.write(user_prompt)

        # ---------------- AGENT ANSWER ----------------

        with st.chat_message("assistant"):

            with st.spinner("Agent is thinking..."):

                response = client.chat.completions.create(

                    model="gpt-4.1-mini",

                    messages=[

                        {
                            "role": "system",

                            "content": """
                                You are a smart PDF Reader Agent developed and maintained by Ejobindia.

                                Rules:

                                1. Answer the user's question ONLY using the uploaded PDF content.

                                2. Do not use your own knowledge.

                                3. Do not guess or invent any answer.

                                4. If the answer is available in the PDF,
                                give a short and clear answer.

                                5. If the answer is NOT available in the PDF,
                                reply exactly:

                                Answer not found in this PDF.

                                6. If the user asks something unrelated to the PDF,
                                reply exactly:

                                I can only help with PDF content.

                                7. Keep every answer short and simple.

                                8. Only provide information that is supported by
                                the uploaded PDF.
                            """
                        },
                        {
                            "role": "user",

                            "content": f"""
                                PDF CONTENT:{pdfContent}
                                USER QUESTION:{user_prompt}
                                Find the answer from the PDF content only.
                            """
                        }

                    ]
                )

                msg = response.choices[0].message.content

            st.write(msg)

        # Save agent message
        st.session_state.messages.append({
            "role": "assistant",
            "content": msg
        })

else:

    st.info("📄 Please upload a PDF to start chatting.")

