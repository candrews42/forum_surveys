

def read_event_information():
    return {
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
    }


def add_question_response():
    return {
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
    }

def read_database_responses():
    return {
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
    }

def submit_survery_results():
    return {
        "type": "function",
        "function": {"name": "submit_survey_result"}
    }

def get_available_tools():
    return [
        read_event_information(),
        add_question_response(),
        read_database_responses(),
    ]