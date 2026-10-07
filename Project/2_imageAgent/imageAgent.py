import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import base64


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OPENAI_API_KEY is not found in .env file")
    st.stop()


# ==========================================
# OPENAI CLIENT
# ==========================================

client = OpenAI(api_key=api_key)


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Image Q&A Agent",
    page_icon="🖼️"
)


# ==========================================
# TITLE
# ==========================================

st.title("🖼️ Image Question Answer Agent")

st.write(
    "Upload an image and ask questions about it."
)


# ==========================================
# CHAT HISTORY
# ==========================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ==========================================
# IMAGE UPLOAD
# ==========================================

uploaded_file = st.file_uploader(
    "📤 Upload an image",
    type=["jpg", "jpeg", "png", "webp"]
)


# ==========================================
# SHOW IMAGE
# ==========================================

if uploaded_file is not None:

    st.image(
        uploaded_file,
        caption="Uploaded Image",
        use_container_width=True
    )


# ==========================================
# DISPLAY OLD CHAT
# ==========================================

for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message("user"):

            st.write(message["content"])


    elif message["role"] == "assistant":

        with st.chat_message("assistant"):

            st.write(message["content"])


# ==========================================
# CHAT INPUT
# ==========================================

question = st.chat_input(
    "Ask a question about the image..."
)


# ==========================================
# WHEN USER SENDS QUESTION
# ==========================================

if question:

    # --------------------------------------
    # CHECK IMAGE
    # --------------------------------------

    if uploaded_file is None:

        st.warning(
            "Please upload an image first."
        )

        st.stop()


    # --------------------------------------
    # SHOW USER QUESTION
    # --------------------------------------

    with st.chat_message("user"):

        st.write(question)


    # --------------------------------------
    # SAVE USER QUESTION
    # --------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    # --------------------------------------
    # READ IMAGE
    # --------------------------------------

    image_bytes = uploaded_file.getvalue()


    # --------------------------------------
    # CONVERT IMAGE TO BASE64
    # --------------------------------------

    base64_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")


    # --------------------------------------
    # IMAGE TYPE
    # --------------------------------------

    image_type = uploaded_file.type


    # --------------------------------------
    # IMAGE URL
    # --------------------------------------

    image_url = (
        f"data:{image_type};base64,{base64_image}"
    )


    # ======================================
    # PROMPT
    # ======================================

    prompt = f"""
You are an Image Question Answering Agent.

Answer ONLY questions that can be answered
from the uploaded image.

User question:

{question}

Rules:

1. Carefully analyze the image.

2. Answer only using information visible
   or clearly understandable from the image.

3. If the question is unrelated to the image,
   answer exactly:

Answer not found in the image.

4. If the required information is not present
   in the image, answer exactly:

Answer not found in the image.

5. Do not use outside knowledge.

6. Do not guess.

7. Do not invent information.

8. Keep the answer simple and clear.
"""


    # ======================================
    # CALL OPENAI
    # ======================================

    with st.chat_message("assistant"):

        with st.spinner("Analyzing image..."):

            try:

                response = client.responses.create(

                    model="gpt-4.1-mini",

                    input=[
                        {
                            "role": "user",

                            "content": [

                                {
                                    "type": "input_text",

                                    "text": prompt
                                },

                                {
                                    "type": "input_image",

                                    "image_url": image_url
                                }

                            ]
                        }
                    ]
                )


                # ------------------------------
                # GET ANSWER
                # ------------------------------

                answer = response.output_text.strip()


                # ------------------------------
                # SHOW ANSWER
                # ------------------------------

                st.write(answer)


                # ------------------------------
                # SAVE ANSWER
                # ------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )


            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )

