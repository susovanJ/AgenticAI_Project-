# 📄 AI CV Builder

AI CV Builder is a simple and user-friendly web application that helps users create a professional and ATS-friendly CV using Artificial Intelligence.

The application is built with **Python, Streamlit, and the OpenAI API**. Users provide their personal information, education, skills, work experience, projects, certifications, and career objective. The application uses AI to improve the wording, correct grammar, organize the information, and generate a professional CV.

## ✨ Features

* 👤 Personal Information
* 🎓 Education
* 🛠️ Skills
* 💼 Work Experience
* 🚀 Projects
* 📜 Certifications
* 🎯 Career Objective
* 🤖 AI-generated professional CV
* 📋 ATS-friendly CV structure
* ✍️ Grammar and content improvement
* 💾 CV saved using Streamlit session state
* ⬇️ Download generated CV as a text file
* 🚫 Prevents AI from intentionally inventing personal information
* 📱 Simple and user-friendly Streamlit interface

## 🛠️ Technologies Used

* **Python**
* **Streamlit**
* **OpenAI API**
* **python-dotenv**

## 🔄 How It Works

The application follows a simple process:

1. The user opens the AI CV Builder application.
2. The user enters their personal information.
3. The user provides their education details.
4. The user enters their skills.
5. The user provides work experience and project details.
6. The user adds certifications and career objectives.
7. The application validates the required information.
8. The information is sent to the OpenAI API through a structured prompt.
9. The AI generates a professional and ATS-friendly CV.
10. The generated CV is displayed in the application.
11. The user can download the generated CV as a `.txt` file.

## 🤖 AI Features

The application uses AI as a professional CV writer.

The AI is instructed to:

* Create a professional CV.
* Keep the CV ATS-friendly.
* Improve grammar.
* Make the content professional.
* Keep the CV concise.
* Use clear section headings.
* Use bullet points where appropriate.
* Avoid inventing information.
* Avoid creating fake companies.
* Avoid creating fake education.
* Avoid creating fake skills.
* Return only the CV without additional explanations.

## 📋 CV Structure

The generated CV follows this structure:

```text
NAME

CONTACT INFORMATION

PROFESSIONAL SUMMARY

CAREER OBJECTIVE

SKILLS

EDUCATION

WORK EXPERIENCE

PROJECTS

CERTIFICATIONS
```

This structure helps keep the generated CV organized and easy to read.

## 🖥️ User Interface

The application provides separate sections for entering CV information:

### 👤 Personal Information

Users can enter:

* Full Name
* Email
* Phone
* Location
* LinkedIn profile

### 🎓 Education

Users can provide their educational qualifications, such as:

```text
MCA - XYZ University - 2025
```

### 🛠️ Skills

Users can enter their technical and professional skills, for example:

```text
Python, SQL, SQLite, OpenAI API, Streamlit, Git
```

### 💼 Work Experience

Users can provide their previous work experience or internships.

### 🚀 Projects

Users can provide information about their academic or personal projects.

### 📜 Certifications

Users can enter their professional or technical certifications.

### 🎯 Career Objective

Users can provide their career goals and objectives.

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
```

Navigate to the project directory:

```bash
cd AI-CV-Builder
```

### 2. Install Required Packages

Install the required Python packages:

```bash
pip install streamlit openai python-dotenv
```

### 3. Create Environment File

Create a `.env` file in the root directory of the project.

Add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key
```

Replace `your_openai_api_key` with your actual API key.

### 4. Run the Application

Run the Streamlit application:

```bash
streamlit run app.py
```

The application will start locally and can be opened in your web browser.

## 📂 Project Structure

```text
AI-CV-Builder/
│
├── app.py
├── .env
├── .gitignore
└── README.md
```

### File Description

| File         | Description                                               |
| ------------ | --------------------------------------------------------- |
| `app.py`     | Main Streamlit application                                |
| `.env`       | Stores the OpenAI API key                                 |
| `.gitignore` | Prevents sensitive/unnecessary files from being committed |
| `README.md`  | Project documentation                                     |

## 🔐 Environment Variables

The application uses an environment variable to securely load the OpenAI API key.

```env
OPENAI_API_KEY=your_openai_api_key
```

The application loads the key using `python-dotenv`:

```python
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
```

The API key is then used to initialize the OpenAI client.

```python
client = OpenAI(api_key=api_key)
```

## ⚠️ Security

**Do not upload your `.env` file to GitHub.**

Add `.env` to your `.gitignore` file:

```gitignore
.env
__pycache__/
*.pyc
```

Never share your OpenAI API key publicly.

If an API key is accidentally exposed, revoke it and create a new one.

## 🧠 OpenAI Integration

The application uses the OpenAI Responses API to generate the CV.

The user's information is combined into a structured prompt and sent to the AI model.

The generated response is then retrieved using:

```python
cv = response.output_text
```

The result is stored in Streamlit session state:

```python
st.session_state["cv"] = cv
```

This allows the generated CV to remain available while the user interacts with the application.

## ✅ Input Validation

The application checks whether important information has been provided before generating the CV.

Currently, the application requires:

* Name
* Email
* Skills

If any required information is missing, an error message is displayed instead of sending the request to the AI.

For example:

```text
Please enter your name.
```

or:

```text
Please enter your email.
```

## ⬇️ Download CV

After generating the CV, users can download it as a text file.

The downloaded file uses the user's name as part of the filename:

```text
Susovan Jana_CV.txt
```

The application uses Streamlit's `download_button` for this functionality.

## 🎯 Project Purpose

The main purpose of this project is to simplify the CV creation process using Artificial Intelligence.

Instead of manually writing and formatting every section of a CV, users can provide their existing information and allow AI to organize and improve the content.

The project is particularly useful for:

* Students
* Freshers
* Job seekers
* Interns
* Developers
* Professionals creating a new CV

The application focuses on transforming **user-provided information** into a more professional CV without intentionally creating fictional qualifications or experience.

## 📌 Example

A user can provide:

```text
Name: Susovan Jana

Education:
MCA - XYZ University - 2025

Skills:
Python, SQL, SQLite, Streamlit, OpenAI API

Experience:
Python Intern

Projects:
AI Chatbot

Certifications:
Python Programming Certificate
```

The AI then organizes this information into a professional CV format.

## 📜 License

This project is available for educational and personal use.

If you want to distribute or modify this project, you can add an appropriate open-source license such as the MIT License.

## 👨‍💻 Author

**Susovan Jana**

Built with:

**Python + Streamlit + OpenAI API 🤖**
