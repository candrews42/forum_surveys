import os
import logging
from datetime import datetime
from typing import Dict
import requests
from pyairtable import Api
from .plugin import Plugin

class AirTablePlugin(Plugin):
    """
    A plugin to interact with Airtable.
    """
    def __init__(self):
        base_id = os.getenv('AIRTABLE_BASE_ID')
        api_key = os.getenv('AIRTABLE_API_KEY')

        if not base_id or not api_key:
            raise ValueError('AIRTABLE_BASE_ID and AIRTABLE_API_KEY environment variables must be set to use AirTablePlugin')

        self.client = Api(api_key)
        self.event_table = self.client.table(base_id, os.getenv('AIRTABLE_TABLE_EVENTS'))
        self.session_table = self.client.table(base_id, os.getenv('AIRTABLE_TABLE_SESSIONS'))
        self.attendees_table = self.client.table(base_id, os.getenv('AIRTABLE_TABLE_ATTENDEES'))
        self.feedback_table = self.client.table(base_id, os.getenv('AIRTABLE_TABLE_FEEDBACK'))
        self.questions_table = self.client.table(base_id, os.getenv('AIRTABLE_TABLE_QUESTIONS'))

    def get_source_name(self) -> str:
        return "Airtable"

    def get_spec(self) -> [Dict]:
        return [
            {
                "name": "read_event_information",
                "description": "Reads event information from the Airtable database including event details, sessions, and attendees.",
                "parameters": {}
            },
            {
                "name": "read_feedback_questions",
                "description": "Reads questions that the event coordinator wants answered from the Airtable database. ALWAYS DO THIS AT THE START OF A CONVERSATION",
                "parameters": {}
            },
            {
                "name": "add_question_response",
                "description": "Adds a question response to the Airtable database in the Feedback table. Be liberal in adding question responses where relevant",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user": {"type": "string", "description": "Name of the user providing the response"},
                        "date": {"type": "string", "description": "Date of the response in YYYY-MM-DD format"},
                        "question_number": {"type": "string", "description": "Identifier for the question being responded to"},
                        "response": {"type": "string", "description": "User's response to the question"}
                    },
                    "required": ["user", "date", "question_number", "response"]
                }
            },
            {
                "name": "read_database_responses",
                "description": "Reads all responses from the Feedback table in the Airtable database.",
                "parameters": {}
            }
        ]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        if function_name == "read_event_information":
            return await self.read_event_information()
        elif function_name == "read_feedback_questions":
            return await self.read_feedback_questions()
        elif function_name == "add_question_response":
            return await self.add_question_response(kwargs['user'], kwargs['date'], kwargs['question_number'], kwargs['response'])
        elif function_name == "read_database_responses":
            return await self.read_database_responses()
        else:
            raise ValueError(f"Function {function_name} not recognized")

    async def read_event_information(self):
        return {
            'events': self.event_table.all(),
            'sessions': self.session_table.all(),
            'attendees': self.attendees_table.all()
        }

    async def read_feedback_questions(self):
        return {
            'questions': self.questions_table.all(),
        }

    async def add_question_response(self, user: str, date: str, question_number: str, response: str):
        """Record a new response."""
        response = self.feedback_table.create({
            'User': user,
            'Date': date,
            'Question #': int(question_number),
            'Response': response
        })
        assert response['id'] is not None
        logging.debug(f"{response['id']} feedback recorded for user {user}")
        return {'status': 'success', 'response_id': response['id']}

    async def read_database_responses(self):
        """Read all responses."""
        responses = self.feedback_table.all()
        return {'responses': responses}
