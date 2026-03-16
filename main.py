import json
import requests
from dotenv import load_dotenv
from langfuse import observe
import google.generativeai as genai
import os


load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")




def clean_json(text):
    text = text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]

    text = text.replace("json", "", 1).strip()

    return text



@observe()
def run_command(command):
    print("🔨 Running command:", command)
    result = os.popen(command).read()
    return result


@observe()
def get_weather(city):
    print("🔨 Weather tool:", city)

    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"

    return "Weather API failed"


@observe()
def create_file(filename):

    print("🔨 Creating file:", filename)

    with open(filename, "w") as f:
        pass

    return f"{filename} created successfully"


@observe()
def write_file(data):

    filename = data["filename"]
    content = data["content"]

    print("🔨 Writing file:", filename)

    with open(filename, "w") as f:
        f.write(content)

    return f"Content written to {filename}"


@observe()
def read_file(filename):

    print("🔨 Reading file:", filename)

    if not os.path.exists(filename):
        return "File not found"

    with open(filename, "r") as f:
        return f.read()


@observe()
def list_files(path="."):

    print("🔨 Listing files")

    return str(os.listdir(path))



available_tools = {
    "run_command": run_command,
    "get_weather": get_weather,
    "create_file": create_file,
    "write_file": write_file,
    "read_file": read_file,
    "list_files": list_files,
}



system_prompt = f"""
    You are an helpfull AI Assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.
    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.
    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}

    Available Tools:
    - get_weather: Takes a city name as an input and returns the current weather for the city
    - run_command: Takes a command as input to execute on system and returns ouput
    
    Example:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "action", "function": "get_weather", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}
"""


messages = [
    {"role": "system", "content": system_prompt}
]




while True:

    user_query = input("> ")

    messages.append({
        "role": "user",
        "content": user_query
    })

    while True:

        prompt = "\n".join(
            [f"{m['role'].upper()}: {m['content']}" for m in messages]
        )

        try:
            response = model.generate_content(prompt)

        except Exception as e:
            print("API Error:", e)
            break


        try:
            cleaned = clean_json(response.text)
            parsed_output = json.loads(cleaned)

        except Exception:
            print("⚠️ Model returned invalid JSON:")
            print(response.text)
            break


        messages.append({
            "role": "assistant",
            "content": json.dumps(parsed_output)
        })


        step = parsed_output.get("step")


   

        if step == "plan":

            print("🧠", parsed_output.get("content"))
            continue




        if step == "action":

            tool_name = parsed_output.get("function")
            tool_input = parsed_output.get("input")

            tool = available_tools.get(tool_name)

            if tool:

                result = tool(tool_input)

                observation = {
                    "step": "observe",
                    "output": result
                }

                messages.append({
                    "role": "assistant",
                    "content": json.dumps(observation)
                })

                continue

            else:
                print("❌ Unknown tool:", tool_name)
                break



        if step == "output":

            print("🤖", parsed_output.get("content"))
            break