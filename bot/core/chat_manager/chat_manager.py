from __future__ import annotations
import datetime

from core.openai.tokens import count_tokens
from core.prompts import get_assistant_prompt


class ChatManager:
    """
    Helper class to manage chat.
    """
    def __init__(self, config: dict) -> None:
        """
        conversations: dict[int: list] { 'chat_id': history }
        conversations_vision: dict[int: bool] { 'chat_id': is_vision }
        last_updated: dict[int: datetime] { 'chat_id': last_updated_timestamp }
        """
        self.conversations: dict[int, list] = {}
        self.conversations_vision: dict[int, bool] = {}
        self.last_updated: dict[int: datetime]
        self.config = config

    def get_conversation_stats(self, chat_id: int) -> tuple[int, int]:
        """
        Gets the number of messages and token used in the converstaion.
        :param chat_id: The Chat ID
        :return: A tuple containing the number of messages and tokens used.
        """
        if chat_id not in self.conversations:
            self.reset_chat_history(chat_id)
        chat = self.conversations[chat_id]
        return (
            len(chat),
            count_tokens(
                model=self.config['model'],
                vision_model=self.config['vision_model'],
                vision_detail=self.config['vision_detail'],
                messages=chat,
            )
        )
    
    def count_chat_tokens(self, chat_id: int) -> int:
        chat = self.conversations[chat_id]
        return count_tokens(
            model=self.config['model'],
            vision_model=self.config['vision_model'],
            vision_detail=self.config['vision_detail'],
            messages=chat,
    )
    
    def reset_chat_history(self, chat_id, content: str =''):
        """
        Resets the conversation history. 
        """
        if content == '':
            content = get_assistant_prompt()
        self.conversations[chat_id] = []
        self.__add_message(chat_id, "system", content)
        self.conversations_vision[chat_id] = False

    def max_age_reached(self, chat_id) -> bool:
        """
        Check if the maximum conversation age has been reached.
        Returns a boolean indication wheather the max conversation age
        has been reached for the provided chat_id
        """
        if chat_id not in self.last_updated:
            return False
        last_updated = self.last_updated[chat_id]
        max_age_minutes = self.config['max_conversation_age_minutes']
        now = datetime.datetime.now()
        return last_updated < now - datetime.timedelta(minutes=max_age_minutes)

    def add_function_call_to_history(
            self,
            chat_id: int,
            function_name: str,
            content: str
        ):
        """
        Adds a function call to the conversation history.
        """
        self.__add_message(chat_id, 'function', content, name=function_name)

    def add_to_history(self, chat_id: int, role: str, content: str):
        """
        Adds a function call to the conversation history.
        """
        self.__add_message(chat_id, role, content)
    
    def __add_message(self, chat_id: int, role: str, content: str, **kwargs):
        """
        Adds a message to the chat.
        """
        message = {
            "role": role,
            "content": content
        }
        for arg, value in kwargs.items():
            message[arg] = value
        self.conversations[chat_id].append(message)

    def update_chat_timestamp(self, chat_id: int):
        self.last_updated[chat_id] = datetime.datetime.now()

    def have_user_chat(self, chat_id: int) -> bool:
        return chat_id in self.conversations
    
    def max_history_reached(self, chat_id: int) -> bool:
        max_history = self.get_max_history()
        user_chat = self.conversations[chat_id]
        return len(user_chat) > max_history
    
    def get_max_history(self) -> int:
        return self.config['max_history_size']

    def get_chat(self, chat_id: int) -> list:
        return self.conversations[chat_id]
    
    def pop_chat(self, chat_id: int) -> None:
        """
        Resizes chat to maintain max_history size
        in a first in first out fashion.
        """
        max_history = self.get_max_history()
        self.conversations[chat_id] = self.conversations[chat_id][-max_history:]

    def init_chat(self, chat_id: int) -> None:
        """
        Makes sure new chat is ready to be inserted.
        """
        if not self.have_user_chat(chat_id) or self.max_age_reached(chat_id):
            self.reset_chat_history(chat_id)
        self.update_chat_timestamp(chat_id)