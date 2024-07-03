from datetime import datetime
import logging

from pyairtable import Api


class AirTable:
    def __init__(self, config: dict):
        base_id = config['base_id']
        self.client = Api(config['api_key'])
        self.event_table = self.client.table(
            base_id,
            config['table_event_details'
        ])
        self.session_table = self.client.table(
            base_id,
            config['table_sessions'
        ])
        self.attendees_table = self.client.table(
            base_id,
            config['table_attendees'
        ])
        self.feedback_table = self.client.table(
            base_id,
            config['table_feedback'
        ])

    def read_event_information(self):
        return (
            self.event_table.all(),
            self.session_table.all(),
            self.attendees_table.all(),
        )
    
    def add_question_response(
            self,
            user: int,
            question_number: int,
            response: str,
    ):
        """Record a new response."""
        response = self.feedback_table.create({
            'User': user,
            'Date': str(datetime.now()),
            'Question #': question_number,
            'Response': response,
        })
        assert response['id'] != None
        logging.debug(f"{response['id']} feedback recorded for user {user}")

    def read_responses(self, user_id):
        """Read responses for a specific user."""
        formula = f"{{user}} = '{user_id}'"
        return self.feedback_table.all(formula=formula)