import openpyxl
import json
import sqlite3
from openpyxl import Workbook
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def save_excel(filename: str):
    # if filename.endswith(".xlsx"):
    #     filename = filename[:-5]

    con = sqlite3.connect("./MY_WORK/Project/4_ExcelProject/Employee.db")
    cursor = con.cursor()
    cursor.execute("select eid,name,salary from Employees")
    data = cursor.fetchall()

    wb = Workbook()
    ws = wb.active
    ws.append([
        "Employeeid",
        "Name",
        "Gross Salary",
        "PF",
        "TDS",
        "NET salary"
    ])

    for eid, name, salary in data:
        eid = eid
        name = name
        Gross_salary = salary
        pf = salary * 0.12
        Tds = salary * 0.12
        Net_salary = salary - pf - Tds

        ws.append([
            eid,
            name,
            Gross_salary,
            pf,
            Tds,
            Net_salary
        ])

    wb.save("./MY_WORK/Project/4_ExcelProject/" + filename + ".xlsx")
    con.close()
    return "create excel successfully"


def exec_query(query: str):
    try:
        con = sqlite3.connect("./MY_WORK/Project/4_ExcelProject/Employee.db")
        cursor = con.cursor()
        cursor.execute(query)
        con.commit()
        con.close()
        return "query execute successfully"
    except Exception as ex:
        print(ex)
        return str(ex)


def read(filename: str):
    # if filename.endswith(".xlsx"):
    #     filename = filename[:-5]

    wb = openpyxl.load_workbook("./MY_WORK/Project/4_ExcelProject/" + filename + ".xlsx")
    ws = wb.active
    data = list(ws.values)
    return str(data)


tools = [
    {
        "type": "function",
        "name": "save_excel",
        "description": "this function is create or update excel sheet",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "excel filename without .xlsx"
                }
            },
            "required": ["filename"]
        }
    },
    {
        "type": "function",
        "name": "exec_query",
        "description": "this function is execute sql query",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "this function is execute sql query"
                }
            },
            "required": ["query"]
        }
    },
    {
        "type": "function",
        "name": "read",
        "description": "this function use read excel sheet",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "excel filename without .xlsx"
                }
            },
            "required": ["filename"]
        }
    }
]

system_inst = """
    You are an Excel management assistant.
    IMPORTANT EXCEL RULES:
    1. CREATE EXCEL
    ----------------
    If the user says:
    - create excel
    - create excel file
    - generate excel
    - generate excel file
    - make excel
    - make excel file
    then use ONLY the save_excel function.
    Do not ask for employee ID.
    The save_excel function creates the Excel file from the Employees database.

    -----------------------------------------------------
    2. UPDATE EXCEL FILE
    -----------------------
    If the user says:
    - update excel
    - update excel file
    - refresh excel
    - refresh excel file
    - regenerate excel
    - regenerate excel file

    then use ONLY the save_excel function.
    "update excel file" means regenerate the Excel file from the current database.
    It does NOT mean update an employee.
    Do NOT ask for employee ID.
    Do NOT use exec_query.

    --------------------------------------------------
    3. READ EXCEL
    ----------------
    If the user asks:
    - read excel
    - show excel
    - show excel data
    - what is in excel
    - employee data in excel
    - salary data in excel
    - any question about the Excel data

    then use the read function.
    Do not use save_excel.

    --------------------------------------------------
    DATABASE:Employees(eid,name,salary)
    -------------------------------------------------
    INSERT:
    If the user explicitly asks to execute an SQL INSERT query:
    - Use only exec_query.
    - Do not use save_excel.
    - Do not use read.
    - Do not ask for ID unless required by the user's query.
    --------------------------------------------------
    UPDATE DATABASE:
    If user execute update query same are present then ask id.
    If the user explicitly asks to execute an SQL UPDATE query:
    - Use only exec_query.
    - Do not use save_excel.
    - Do not use read.

    If multiple employees have the same name, ask for employee ID.

    --------------------------------------------------
    DELETE EMPLOYEE ID RANGE:
    If the user asks to delete a range of employee IDs, for example:
    - delete employee eid = 11 to 20
    - delete employee id 11 to 20
    - delete employees from 11 to 20
    - delete employee ids 11 to 20
    then:
    1. Do NOT ask for employee names.
    2. Do NOT ask for confirmation.
    3. Immediately execute the delete operation.
    4. Delete all employees whose eid is between the given starting ID and ending ID.
    5. Renumber the remaining employee IDs so there are NO gaps.
    6. Reset the AUTOINCREMENT sequence after renumbering.
    7. Use exec_query.
    8. Do not use save_excel.
    9. Do not use read.

    Example:
    User:delete employee eid = 11 to 20
    Execute immediately:
    DELETE FROM Employees
    WHERE eid BETWEEN 11 AND 20;

    UPDATE Employees
    SET eid = (
        SELECT COUNT(*)
        FROM Employees e2
        WHERE e2.eid <= Employees.eid
    );

    UPDATE sqlite_sequence
    SET seq = (
        SELECT COALESCE(MAX(eid), 0)
        FROM Employees
    )
    WHERE name = 'Employees';

    Do not ask for any employee name.

    --------------------------------------------------
    DELETE ONE EMPLOYEE:
    If the user asks to delete ONE employee:
    1. Employee ID is required.
    2. Employee name is required for verification.
    3. If the user gives only the employee ID:
    - Ask only for the employee name.
    - Do not delete yet.
    - Do not ask for confirmation.

    Example:
    User:
    delete employee id=14

    Assistant:
    Please enter the employee name for ID 14.

    4. If the user then provides the employee name:
    - Immediately execute the delete operation.
    - Do not ask for confirmation.

    5. The delete operation must:
    - Delete the employee matching BOTH eid and name.
    - Renumber the remaining employee IDs so there are NO gaps.
    - Reset the AUTOINCREMENT sequence after renumbering.

    6. Use exec_query.
    7. Do not use save_excel.
    8. Do not use read.

    Example:
    If database contains:
    1 - Amit
    2 - Ram
    3 - John
    4 - Sita

    User:delete employee id=2
    User:Ram

    Then delete Ram and renumber:
    1 - Amit
    2 - John
    3 - Sita

    The next employee ID should continue from the current highest ID.
    IMPORTANT:
    After the user provides the name, immediately execute the delete operation.
    Do not ask for confirmation.

    --------------------------------------------------
    DELETE ONE EMPLOYEE SQL:

    For a single employee deletion, use the following SQL logic:

    DELETE FROM Employees
    WHERE eid = 14 AND name = 'Ram';

    UPDATE Employees
    SET eid = (
        SELECT COUNT(*)
        FROM Employees e2
        WHERE e2.eid <= Employees.eid
    );

    UPDATE sqlite_sequence
    SET seq = (
        SELECT COALESCE(MAX(eid), 0)
        FROM Employees
    )
    WHERE name = 'Employees';

    IMPORTANT:

    These statements are ONLY for deleting one employee and renumbering IDs.

    The employee DELETE must check both eid and name.

    --------------------------------------------------
    DELETE ALL EMPLOYEES:
    If the user explicitly asks to delete ALL employees:
    Use exec_query.
    Execute:
    DELETE FROM Employees;

    DELETE FROM sqlite_sequence
    WHERE name = 'Employees';

    All employee data must be deleted and the sequence must be reset.

    --------------------------------------------------
    IMPORTANT DISTINCTION:
    "update excel file"
    means:
    save_excel()

    "update employee salary"
    means:
    exec_query()

    "update employee"
    means:
    database employee update.

    "delete employee"
    means:
    delete employee by ID and name.

    "delete employee eid 11 to 20"
    means:
    delete all employees from ID 11 through ID 20 without asking for names.

    Do not confuse updating the Excel file with updating an employee.

    --------------------------------------------------
    FILE NAME:
    The filename passed to save_excel and read must NOT contain .xlsx.

    --------------------------------------------------
    ONLY ANSWER QUESTIONS RELATED TO:
    - Excel
    - Excel files
    - Employees
    - Employee database
    - Employee salary
    - SQL operations on Employees

    For unrelated questions respond exactly:
    I dont Know.
"""


message = []

while True:
    user_input = input("You:")

    if user_input.lower() in ["exit"]:
        print("AGENT:BYE....")
        exit()
    else:
        message.append({
            "role": "user",
            "content": user_input
        })

        res = client.responses.create(
            model="gpt-4.1",
            instructions=system_inst,
            input=message,
            tools=tools
        )

        for item in res.output:
            if item.type == "function_call":
                arguments = json.loads(item.arguments)
                if item.name == "save_excel":
                    filename = arguments["filename"]
                    result = save_excel(filename)
                    print("AGENT:", result)

                    message.append(item)

                    message.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": result
                    })

                elif item.name == "exec_query":
                    query = arguments["query"]
                    result = exec_query(query)
                    print("AGENT:", result)
                    message.append(item)

                    message.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": result
                    })

                elif item.name == "read":
                    filename = arguments["filename"]
                    result = read(filename)
                    message.append(item)

                    message.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": result
                    })

                    res = client.responses.create(
                        model="gpt-4.1",
                        instructions=system_inst,
                        input=message,
                        tools=tools
                    )

                    print("AGENT:", res.output_text)

            else:
                print("AGENT:", res.output_text)