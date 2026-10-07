import json
import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

load_dotenv()

client = OpenAI()

PDF_FOLDER = "./MY_WORK/Project/5_PdfFile_Agent"
CHILD_PDF_NAME = "agent_answers"

os.makedirs(PDF_FOLDER, exist_ok=True)

def get_pdf_path(filename):
    filename = filename.replace(".pdf", "")
    return os.path.join(PDF_FOLDER,f"{filename}.pdf")

#================= GET EXISTING PDF NAMES =====================
def list_pdfs():
    pdfs = []
    for file in os.listdir(PDF_FOLDER):
        if file.lower().endswith(".pdf"):
            name = file[:-4]
            pdfs.append(name)
    return pdfs

#=============== FIND RELATED EXISTING PDF =================
def find_related_pdf(user_input):
    pdfs = list_pdfs()

    # Do not use child PDF as parent PDF
    pdfs = [
        pdf for pdf in pdfs
        if pdf.lower() != CHILD_PDF_NAME.lower()
    ]

    if not pdfs:
        return None

    text = user_input.lower()

    # First check exact PDF name inside user message
    for pdf_name in pdfs:
        if pdf_name.lower() in text:
            return pdf_name

    # Check words from PDF filename
    words = re.findall(r"[a-zA-Z0-9]+",text)

    for pdf_name in pdfs:
        pdf_words = re.findall(r"[a-zA-Z0-9]+",pdf_name.lower())
        for word in pdf_words:
            if word in words:
                return pdf_name    
    return None

#===================== READ PDF ========================
def read(filename):
    pdf_path = get_pdf_path(filename)
    if not os.path.exists(pdf_path):
        return None

    reader = PdfReader(pdf_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


#==================== CHECK BLANK PAGE =====================
def is_page_blank(page):
    try:
        text = page.extract_text()
        if text and text.strip():
            return False
        return True
    except Exception:
        return False

#================== GET LAST TEXT Y POSITION ======================
def get_last_y(page):
    positions = []
    try:
        def visitor_text(text,cm,tm,font_dict,font_size):
            if text and text.strip():
                positions.append(tm[5])

        page.extract_text(
            visitor_text=visitor_text
        )

    except Exception:
        return None

    if not positions:
        return None

    return min(positions)

#====================== CREATE NEW CONTENT PDF ====================
def create_content_pdf(width,height,content,start_y):
    temp_path = os.path.join(PDF_FOLDER,"_temp_content.pdf")
    
    pdf = canvas.Canvas(
        temp_path,
        pagesize=(width, height)
    )
    y = start_y
    line_height = 20

    for line in content.split("\n"):
        if y < 40:
            pdf.showPage()
            y = height - 50

        pdf.drawString(50,y,line)
        y -= line_height

    pdf.save()
    return temp_path


def save_file(filename,content):
    filename = filename.replace(".pdf","")
    pdf_path = get_pdf_path(filename)

    if not os.path.exists(pdf_path):
        pdf = canvas.Canvas(
            pdf_path,
            pagesize=(595, 842)
        )
        width = 595
        height = 842
        y = height - 50

        for line in content.split("\n"):
            if y < 40:
                pdf.showPage()
                y = height - 50

            pdf.drawString(50,y,line)
            y -= 20

        pdf.save()

        return (
            f"PDF created successfully: "
            f"{filename}.pdf"
        )

    reader = PdfReader(
        pdf_path
    )
    writer = PdfWriter()
    remaining_lines = content.split("\n")

    for page_index, page in enumerate(reader.pages):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        
        if is_page_blank(page):
            start_y = height - 50

        else:
            last_y = get_last_y(page)
            if last_y is None:
                writer.add_page(page)
                continue

            # Put new data below old data
            start_y = last_y - 25

        available_lines = int((start_y - 40) / 20)

        if available_lines <= 0:
            writer.add_page(page)
            continue

        current_lines = remaining_lines[:available_lines]
        remaining_lines = remaining_lines[available_lines:]
        new_content = "\n".join(current_lines)

        overlay_path = create_content_pdf(width,height,new_content,start_y)
        overlay_reader = PdfReader(overlay_path)
        overlay_page = (overlay_reader.pages[0])

        page.merge_page(overlay_page)
        writer.add_page(page)

        if os.path.exists(overlay_path):
            os.remove(overlay_path)

        if not remaining_lines:
            for remaining_page in reader.pages[page_index + 1:]:
                writer.add_page(remaining_page)

            with open(pdf_path,"wb") as output_file:
                writer.write(output_file)

            return (
                f"Data appended successfully "
                f"to {filename}.pdf"
            )

    # EXISTING PAGES ARE FULL CREATE NEW PAGE
    if remaining_lines:
        first_page = reader.pages[0]
        width = float(first_page.mediabox.width)
        height = float(first_page.mediabox.height)

        new_page_path = create_content_pdf(
            width,
            height,
            "\n".join(remaining_lines),
            height - 50
        )

        new_reader = PdfReader(new_page_path)

        for new_page in new_reader.pages:
            writer.add_page(new_page)

        if os.path.exists(new_page_path):
            os.remove(new_page_path)

    # SAVE FINAL PDF
    with open(pdf_path,"wb") as output_file:
        writer.write(output_file)

    return (
        f"Data appended successfully "
        f"to {filename}.pdf"
    )


tools = [
    {
        "type": "function",
        "name": "save_file",
        "description": """
            Create a PDF or append data to an existing PDF.
            IMPORTANT:
            Never delete existing PDF data.
            Never overwrite existing PDF data.
            If an existing related PDF is provided by the
            Python program, use that filename.
            Always append new data to an existing PDF.
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": """
                        PDF filename WITHOUT .pdf
                    """
                },
                "content": {
                    "type": "string",
                    "description": """
                        New content to write into the PDF.
                    """
                }
            },
            "required": ["filename","content"]
        }
    }
]

system_instr = """
    You are a PDF Agent.
    There are two types of PDF:
    1. Parent PDF
    2. Child PDF

    =========================================================
    PARENT PDF
    =========================================================
    Parent PDFs contain the user's actual information.
    Examples:
    python.pdf
    java.pdf
    sql.pdf

    =========================================================
    IMPORTANT PDF RULE
    =========================================================
    If a related existing PDF already exists:
    DO NOT create a new PDF.
    Append the new content to the existing PDF.
    Never delete old content.
    Never overwrite old content.
    Example:
    Existing:
    python.pdf
    User:
    write python related 50 lines
    The Python program will provide the existing filename.
    Use that filename.
    Do NOT create:
    python1.pdf
    python_new.pdf
    python2.pdf

    =========================================================
    WRITING
    =========================================================
    If the user asks to write content:
    Use save_file.
    The Python program decides whether an existing PDF
    should be reused.
    Never invent a different filename when the Python
    program provides an existing filename.

    =========================================================
    QUESTION ANSWERING
    =========================================================
    The Python program identifies the relevant parent PDF.
    The PDF content is then provided to you.
    Answer ONLY from that PDF content.
    If the answer is not in the PDF, return exactly:
    I could not find the answer in the PDF.

    =========================================================
    CHILD PDF
    =========================================================
    The child PDF is:
    agent_answers.pdf
    When a parent PDF question is answered successfully,
    the Python program asks the user:
    Do you want to save this question and answer as a PDF?
    If the user says yes:
    Append the Q&A to agent_answers.pdf.
    Never delete old Q&A.
    Never overwrite old Q&A.
    If the user says no:
    Do not save.
"""

last_question = ""
last_answer = ""
answer_found = False

while True:
    user_input = input("YOU: ").strip()

    if user_input.lower() in  ["exit","quit"]:
        print("AGENT: BYE....")
        break

    if user_input.lower() == "yes":

        if (answer_found and last_question and last_answer):
            qa_content = (
                f"Question: {last_question}\n"
                f"Answer: {last_answer}"
            )

            result = save_file(CHILD_PDF_NAME,qa_content)
            print("AGENT:",result)

            last_question = ""
            last_answer = ""
            answer_found = False

        else:
            print("AGENT: Nothing to save.")

        continue


    if user_input.lower() == "no":
        if answer_found:
            print(
                "AGENT: The question and answer "
                "were not saved."
            )

            last_question = ""
            last_answer = ""
            answer_found = False

        else:
            print("AGENT: Okay.")

        continue

    existing_pdf = find_related_pdf(user_input)

    question_words = ["what","who","why","when","where","how","which","explain","define","tell me"]

    is_question = any(
        word in user_input.lower()
        for word in question_words
    )

    if is_question:
        if existing_pdf is None:
            print("AGENT: I could not find the answer in the PDF.")
            continue

        pdf_content = read(existing_pdf)

        if not pdf_content:
            print("AGENT: I could not find the answer in the PDF.")
            continue

        question_prompt = f"""
            Answer the user's question using ONLY
            the following PDF content.
            PDF:{existing_pdf}.pdf
            CONTENT:{pdf_content}
            USER QUESTION:{user_input}
            RULES:
            1. Use only the PDF content.
            2. Do not use outside knowledge.
            3. If the answer is found, answer it.
            4. If the answer is not found, return exactly:
            I could not find the answer in the PDF.
        """

        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=question_prompt,
            input=user_input
        )

        final_answer = (
            response.output_text.strip()
        )

        print("AGENT:",final_answer)

        if (final_answer.lower()!="i could not find the answer in the pdf."):
            last_question = user_input
            last_answer = final_answer
            answer_found = True
            print("Do you want to save this question and answer as a PDF (yes/no)?")
        else:

            last_question = ""
            last_answer = ""
            answer_found = False

        continue

    if existing_pdf:
        write_instruction = f"""
                {system_instr}
                IMPORTANT:
                An existing related PDF has already been found:
                {existing_pdf}.pdf
                The user wants to add content related to this PDF.
                You MUST use this exact filename:{existing_pdf}
                Do NOT create another filename.
                Do NOT add .pdf to the filename.
                Use save_file with:filename = "{existing_pdf}"
                The Python program will append the new content.
            """

    else:
        write_instruction = system_instr

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=write_instruction,
        input=user_input,
        tools=tools
    )

    function_called = False
    for item in response.output:
        if item.type == "function_call":
            function_called = True
            arguments = json.loads(item.arguments)

            if item.name == "save_file":
                filename = arguments["filename"]
                content = arguments["content"]
                filename = filename.replace(".pdf","")

                if existing_pdf:
                    filename = existing_pdf

                result = save_file(filename,content)
                print("AGENT:",result)

    if not function_called:
        print("AGENT:",response.output_text)

