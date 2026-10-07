from openai import OpenAI
from dotenv import load_dotenv
import os
import streamlit as st


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)


st.set_page_config(
    page_title="Wikipedia Agent",
    page_icon="📚"
)

st.title("📚 Wikipedia Research Agent")

wikipedia_url = "https://en.wikipedia.org/wiki/Java_(programming_language)"


# -----------------------------
# Chat history
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# Show old messages
# -----------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])


question = st.chat_input("Ask your question...")


if question:

    # Show user question
    with st.chat_message("user"):
        st.write(question)

    # Save question
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })


    # -----------------------------
    # Prompt
    # -----------------------------

    prompt = f"""
        You are a Wikipedia research ChatBot.

        Use this Wikipedia page:

        {wikipedia_url}

        Search the web and find information from this
        Wikipedia page.

        Answer the user's question.

        Question:
        {question}

        Rules:
        - Use information from the provided Wikipedia page.
        - Do not make up information.
        - Give a simple and clear answer wikipedia page not found.
    """


    with st.spinner("Searching Wikipedia..."):

        response = client.responses.create(
            model="gpt-4.1-mini",

            tools=[
                {
                    "type": "web_search"
                }
            ],

            input=prompt
        )


    answer = response.output_text


    
    # Show answer
    
    with st.chat_message("assistant"):
        st.write(answer)


    # Save answer
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })