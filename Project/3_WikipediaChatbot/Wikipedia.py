from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)


wikipedia_url = input("Enter Wikipedia URL: ")

while True:
    question = input("Ask your question: ")

    prompt = f"""
        You are a Wikipedia research agent.
        The user provided this Wikipedia URL:
        {wikipedia_url}
        Search the web and find information from this
        Wikipedia page.
        Then answer the user's question.
        Question:
        {question}
        Rules:
        - Use information from the provided Wikipedia page.
        - Do not make up information.
        - Give a simple and clear answer.
    """

   
    response = client.responses.create(
        model="gpt-4.1-mini",

        tools=[
            {
                "type": "web_search"
            }
        ],

        input=prompt
    )

    print(f"Agent: {response.output_text}")