import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)


st.set_page_config(
    page_title="AI CV Builder",
    page_icon="📄",
    layout="wide"
)


# ==================================================
#   TITLE
# ==================================================

st.title("📄 AI CV Builder")

st.write(
    "Fill in your details and let AI create your professional CV."
)


# ==================================================
# CV FORM
# ==================================================

with st.form("cv_form"):

    st.header("👤 Personal Information")

    name = st.text_input(
        "Full Name",
        placeholder="Example: Susovan Jana"
    )

    email = st.text_input(
        "Email",
        placeholder="Example: susovan@gmail.com"
    )

    phone = st.text_input(
        "Phone",
        placeholder="Example: +91 9876543210"
    )

    location = st.text_input(
        "Location",
        placeholder="Example: Kolkata, India"
    )

    linkedin = st.text_input(
        "LinkedIn",
        placeholder="Example: linkedin.com/in/yourname"
    )


    st.header("🎓 Education")

    education = st.text_area(
        "Education",
        placeholder="Example: MCA - XYZ University - 2025"
    )

    st.header("🛠️ Skills")

    skills = st.text_area(
        "Skills",
        placeholder="Python, SQL, SQLite, OpenAI API, Streamlit, Git"
    )

    st.header("💼 Experience")

    experience = st.text_area(
        "Work Experience",
        placeholder="Example:Python Intern"
    )

    st.header("🚀 Projects")

    projects = st.text_area(
        "Projects",
        placeholder="Example:AI Chatbot"
    )


    st.header("📜 Certifications")

    certifications = st.text_area(
        "Certifications",
        placeholder="Example: Python Programming Certificate"
    )


    st.header("🎯 Career Objective")

    objective = st.text_area(
        "Career Objective",
        placeholder=(
            "Example: Looking for an opportunity to work as a Python developer..."
        )
    )


    generate_button = st.form_submit_button(
        "✨ Generate Professional CV"
    )


# ==================================================
# GENERATE CV
# ==================================================

if generate_button:

    # ------------------------------------------------
    # VALIDATION
    # ------------------------------------------------

    if name == "":
        st.error("Please enter your name.")

    elif email == "":
        st.error("Please enter your email.")

    elif skills == "":
        st.error("Please enter your skills.")

    else:

        # ------------------------------------------------
        # OPENAI PROMPT
        # ------------------------------------------------

        prompt = f"""You are a professional CV writer.
            Create a professional and ATS-friendly CV.

            IMPORTANT RULES:
            1. Do not invent information.
            2. Do not add fake companies.
            3. Do not add fake education.
            4. Do not add fake skills.
            5. Improve grammar.
            6. Make the content professional.
            7. Keep the CV concise.
            8. Use clear section headings.
            9. Use bullet points where appropriate.
            10. Return only the CV.
            11. Do not add explanations.
            12. Do not use Markdown code blocks.

            Use this structure:
            NAME
            CONTACT INFORMATION
            PROFESSIONAL SUMMARY
            CAREER OBJECTIVE
            SKILLS
            EDUCATION
            WORK EXPERIENCE
            PROJECTS
            CERTIFICATIONS
            PERSONAL INFORMATION:

            Name:{name}
            Email:{email}
            Phone:{phone}
            Location:{location}
            LinkedIn:{linkedin}
            CAREER OBJECTIVE:{objective}
            EDUCATION:{education}
            SKILLS:{skills}
            WORK EXPERIENCE:{experience}
            PROJECTS:{projects}
            CERTIFICATIONS:{certifications}
        """

        try:
            with st.spinner("🤖 AI is creating your CV..."):
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=prompt
                )
                cv = response.output_text


            # ------------------------------------------------
            # SAVE IN SESSION
            # ------------------------------------------------
            st.session_state["cv"] = cv
            st.success("✅ CV generated successfully!")

        except Exception as e:
            st.error(f"Error: {e}")


# ==================================================
# DISPLAY CV
# ==================================================

if "cv" in st.session_state:
    st.divider()
    st.header("📄 Your Professional CV")
    cv = st.session_state["cv"]

    # ------------------------------------------------
    # DISPLAY CV
    # ------------------------------------------------
    with st.container(border=True):
        st.markdown(cv)

    # ------------------------------------------------
    # DOWNLOAD CV
    # ------------------------------------------------

    st.download_button(
        label="⬇️ Download CV",
        data=cv,
        file_name=f"{name}_CV.txt",
        mime="text/plain"
    )