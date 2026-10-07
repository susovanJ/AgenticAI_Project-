from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader
import os

load_dotenv()

client = OpenAI()

reader = PdfReader("./Ejobindia.pdf")

pdfContent = "" 
for page in reader.pages:
    pdfContent += page.extract_text()


while True:
    user_prompt = input("You: ")
    if user_prompt.lower() in ['exit','quit']:
        print("Agent: Thanks for visiting!")
        exit(0)
        
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role":"system",
                "content":'''
                -You are a smart PDF Reader Agent who can summarize and answer questions answer from pdf content'
                -short answer for every question
                -If User asks something apart from specified pdf , then reply "I can only help with pdf content"
                -Developed & Maintained by Ejobindia
                '''
            },
            {
                "role":"user",
                "content":f'''
                for question using {user_prompt}, and context using {pdfContent}
                '''
            }
        ]
    )
    msg = response.choices[0].message.content
    print("Agent:",msg)