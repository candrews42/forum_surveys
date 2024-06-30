import openai
import requests

# Set up OpenAI API key
openai.api_key = 'OPENAI_API_KEY'

# Airtable API key and base ID
AIRTABLE_API_KEY = 'AIRTABLE_API_KEY'
BASE_ID = 'appW1s23YY2JwLkmq'

# Function to read event information
def read_event_information():
    event_details_url = f'https://api.airtable.com/v0/{BASE_ID}/tblBA6ebOewcLAP7Q'
    sessions_url = f'https://api.airtable.com/v0/{BASE_ID}/tblT4ZEfbgR8EpbJw'
    attendees_url = f'https://api.airtable.com/v0/{BASE_ID}/tbljlZbnWjpQHrdY2'

    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
    }

    event_details_response = requests.get(event_details_url, headers=headers).json()
    sessions_response = requests.get(sessions_url, headers=headers).json()
    attendees_response = requests.get(attendees_url, headers=headers).json()

    return {
        'Event Details': event_details_response,
        'Sessions': sessions_response,
        'Attendees': attendees_response
    }

# Function to add question response to the database
def add_question_response(user, date, question_number, response):
    feedback_raw_url = f'https://api.airtable.com/v0/{BASE_ID}/tblHxRQEDXsri8MWT'
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'fields': {
            'User': user,
            'Date': date,
            'Question #': question_number,
            'Response': response
        }
    }
    response = requests.post(feedback_raw_url, headers=headers, json=data)
    return response.json()

# Function to read database of responses
def read_database_responses():
    feedback_raw_url = f'https://api.airtable.com/v0/{BASE_ID}/tblHxRQEDXsri8MWT'
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
    }
    response = requests.get(feedback_raw_url, headers=headers).json()
    return response

# Example usage
event_info = read_event_information()
print("Event Information:", event_info)

# Adding a question response
add_response_result = add_question_response("User1", "2024-06-30", "Q1", "Great event!")
print("Add Response Result:", add_response_result)

# Reading the database of responses
responses = read_database_responses()
print("Database Responses:", responses)

# Function to handle OpenAI tool interaction
def chatbot_using_tools(input):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "read_event_information",
                "description": "Reads event information from the Airtable database including event details, sessions, and attendees",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_question_response",
                "description": "Adds a question response to the Airtable database in the Feedback Raw table",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user": {
                            "type": "string",
                            "description": "Name of the user providing the response",
                        },
                        "date": {
                            "type": "string",
                            "description": "Date of the response in YYYY-MM-DD format",
                        },
                        "question_number": {
                            "type": "string",
                            "description": "Identifier for the question being responded to",
                        },
                        "response": {
                            "type": "string",
                            "description": "User's response to the question",
                        },
                    },
                    "required": ["user", "date", "question_number", "response"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_database_responses",
                "description": "Reads all responses from the Feedback Raw table in the Airtable database",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            }
        },
    ]
    client = OpenAI(api_key=openai_api_key)
    # Generate response from GPT
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=st.session_state["messages"],
        stream=False,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "submit_survey_result"}},
    )

    print("tool call results")
    print(response.choices[0].message.tool_calls[0].function.arguments)
    arguments = response.choices[0].message.tool_calls[0].function.arguments
    # Parse the JSON string into a dictionary
    arguments_dict = json.loads(arguments)

    # Format the survey results
    formatted_results = [
        {"question_num": f"q{i+6}", "question": question}
        for i, question in enumerate(arguments_dict.values())
    ]

    print(f"Formatted results: {formatted_results}")

    # Add the formatted results to the database
    add_forum(formatted_results)
    
    return response

# Example OpenAI tool interaction
response = chatbot_using_tools(input)
print("OpenAI Tool Response:", response)



