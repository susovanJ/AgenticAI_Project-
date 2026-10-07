import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from openai import OpenAI
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def send_email(reciever:str,subject:str,body:str):
    sender = os.getenv("EMAIL_ID")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender or not sender_password:
        return "Email not sent: EMAIL_ID and EMAIL_PASSWORD are not configured."
    
    message = MIMEText(body)
    message['subject'] = subject
    message['from'] = sender
    message['to'] = reciever

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, sender_password)
            server.send_message(message)
            return "Email sent successfully!"
    except Exception as ex:
        print(f"SMTP error: {ex}")
        return f"Email not sent: {ex}"
    
# response = send_email("susovanjana456@gmail.com","Test Mail","Hello susovan.")
# print(response)

#Tool Create
tools=[{
    "type":"function",
    "function":{
        "name":"send_email",
        "description":"This function or tool is used to send email exracted reciever , subject and body from the prompt.use this tool whenever user asks to send email Create an correct content based on body provided by the useras a prompt.",
        "parameters":{
            "type":"object",
            "properties":{
                "reciever":{"type":"string"},
                "subject":{"type":"string"},
                "body":{"type":"string"}
            },
            "required":["reciever","body","subject"]
        }
    }
}]

#Email Sent Loop
while True:
    user_prompt = input("Please provide reciever email id, body, and subject: ")
    if user_prompt.lower() in ['exit','quit']:
        print("Agent: Bye!")
        exit(0)

    responses = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role":"system",
                "content":'''
                -You are an email sending Agent
               -Who will send the email using defined tools
               by constructing small & proper sentences using
               reciever , subject, body extracted from the prompt.
               Whenever user ask to send mail please use defined tools,
               oterwise say "I can only help with sending mails".
                '''
            },
            {
                "role":"user",
                "content":user_prompt
            }
        ],
        tools=tools
    )

    msg = responses.choices[0].message
    if msg.tool_calls:
        tool_name = msg.tool_calls[0].function.name
        tools_arg = json.loads(msg.tool_calls[0].function.arguments)
        if tool_name == "send_email":
            result = send_email(
                tools_arg["reciever"],
                tools_arg["subject"],
                tools_arg["body"]
            )
            print(f"Agent: {result}")
        else:
            print("Agent: Error! Tool not recognized.")
    else:
        print("Agent: Error! No tool call was made.")