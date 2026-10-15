from openai import OpenAI
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

st.set_page_config(
    page_title="Wikipedia ChatBot",
    page_icon="📚"
)

st.title("📚 Wikipedia Research ChatBot")

#=============== Wikipedia URL input ===============
wikipedia_url = st.text_input(
    "Wikipedia link",
    value="",
    placeholder="Enter Wikipedia URL..."
)

#================== Chat history ===================
if "messages" not in st.session_state:
    st.session_state.messages = []

#================== Show old messages ==================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Ask your question...")
if question:
    # Check: Is the URL valid?
    # The link must start with "https://" and must contain "wikipedia.org".
    # If either condition fails, show an error message to the user.
    if not wikipedia_url.startswith("https://") or "wikipedia.org" not in wikipedia_url:
        st.error("Please enter a valid Wikipedia link.")
    
    else:
        #================ Show user question ==============
        with st.chat_message("user"):
            st.write(question)

        #================ Save question =================
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        #=============== Prompt ===================
        prompt = f"""
            You are a Wikipedia research ChatBot.
            Use this Wikipedia page:{wikipedia_url}
            Search the web and find information from this
            Wikipedia page.
            Answer the user's question.
            Question:{question}
            
            Rules:
            - Use information from the provided Wikipedia page.
            - Do not make up information.
            - If the Wikipedia page is not found, say that clearly.
            - Give a simple and clear answer.
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

        #=========== Show answer ================
        with st.chat_message("assistant"):
            st.write(answer)

        #========== Save answer =============
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })