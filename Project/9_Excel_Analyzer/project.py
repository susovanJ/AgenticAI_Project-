
#! STEP 1: Import the required libraries
# Used to connect to the OpenAI AI model.
from openai import OpenAI

# Used to load the API key from the .env file.
from dotenv import load_dotenv

# Used to access environment variables and check files.
import os

# Used to convert JSON strings into Python data.
import json

# Workbook creates a new Excel file.
# load_workbook opens an existing Excel file.
from openpyxl import Workbook, load_workbook

#! STEP 2: Load the API key
# Read the variables stored in the .env file.
load_dotenv()

# Get the API key and create an OpenAI client.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Display a connection message.
print("OpenAI Connected")


#! STEP 3: Create an Excel file
def create_excel(headers: list, rows: list) -> str:
    # This function creates an Excel file.
    # headers contains the column names.
    # rows contains the Excel data.

    # Start error handling.
    try:
        # Create a new Excel workbook.
        wb = Workbook()

        # Select the active worksheet.
        wb_sheet = wb.active

        # Set the worksheet name.
        wb_sheet.title = "sheet1"

        # Add column headings to the first row.
        wb_sheet.append(headers)

        # Take each data row one by one.
        for row in rows:
            # Add the current row to Excel.
            wb_sheet.append(row)

        # Save the workbook as test.xlsx.
        wb.save("./MY_WORK/Project/9_Excel_Analyzer/test.xlsx")
        wb.close()

        # Return a success message.
        return "Excel file created successfully."

    # Catch any error during Excel creation.
    except Exception as ex:
        # Return the error message.
        return f"Error: {str(ex)}"


#! STEP 4: Read the Excel file

# This function reads data from test.xlsx.
def read_excel() -> str:
    # Start error handling.
    try:
        # Check whether the Excel file exists.
        if not os.path.exists(
            "./MY_WORK/Project/9_Excel_Analyzer/test.xlsx"
        ):
            # Stop if the file is missing.
            return "File does not exist."

        # Open the Excel file.
        # data_only=True reads saved formula results when available.
        wb = load_workbook(
            "./MY_WORK/Project/9_Excel_Analyzer/test.xlsx",
            data_only=True
        )

        # Read all rows and cells from the active sheet.
        data = list(wb.active.values)

        # Close the Excel workbook.
        wb.close()

        # Convert the data into a JSON string.
        return json.dumps(data, default=str)

    # Catch any error while reading Excel.
    except Exception as ex:
        # Return the error message.
        return f"Error: {str(ex)}"


#! STEP 5: Define the tools available to the AI
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_excel",
            "description": "Create an Excel file named test.xlsx.",
            "parameters": {
                "type": "object",
                "properties": {
                    "headers": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Column headings for Excel."
                    },
                    "rows": {
                        "type": "array",
                        "items": {
                            "type": [
                                "number",
                                "string",
                                "boolean",
                                "null"
                            ]
                        },
                        "description": "Data rows for Excel."
                    }
                },
                "required": ["headers", "rows"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_excel",
            "description": "Read the content of test.xlsx.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


#! STEP 6: Start the user conversation
# Keep accepting user instructions until exit.
while True:
    # Read the user's message and remove extra spaces.
    user_input = input("You: ").strip()

    # Check whether the user wants to stop.
    if user_input.lower() in ["exit", "quit"]:
        # Display a goodbye message.
        print("Agent: Bye")
        # Stop the loop.
        break

    #! STEP 7: Send the instruction to the AI
    messages = [
        {
            "role": "system",
            "content": """
                You are an Excel file agent.
                You can:
                1. Create test.xlsx using create_excel.
                2. Read test.xlsx using read_excel.

                Rules:
                - If the user requests Excel creation, call create_excel.
                - If the user asks any question about existing Excel data,
                ALWAYS call read_excel first.
                - Answer questions about student IDs, names, or other records
                only using the data returned by read_excel.
                - If the requested record exists, return the matching information.
                - If the record does not exist, clearly say that no matching
                record was found.
                - Never guess or invent Excel data.
            """
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    #! STEP 8: Check the AI response and process tool calls
    while True:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        msg = response.choices[0].message

        if not msg.tool_calls:
            print("Agent:", msg.content)
            break

        # Add the assistant's tool-call message to the conversation.
        messages.append(msg)

        #! STEP 9: Execute the requested function
        for tool_call in msg.tool_calls:
            tool_name = tool_call.function.name

            try:
                tools_arg = json.loads(tool_call.function.arguments)

                if tool_name == "create_excel":
                    result = create_excel(
                        tools_arg["headers"],
                        tools_arg["rows"]
                    )

                elif tool_name == "read_excel":
                    result = read_excel()

                else:
                    result = "Error! Tool not recognized."

            except Exception as ex:
                result = f"Error: {str(ex)}"

            # Send the tool result back to the AI.
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

            # Display creation results immediately.
            if tool_name == "create_excel":
                print(f"Agent: {result}")


