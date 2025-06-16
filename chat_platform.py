from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from slack_bolt import App
import os

class ChatPlatform(ABC):
    @abstractmethod
    def send_message(self, channel: str, text: str, thread_ts: Optional[str] = None):
        pass

    @abstractmethod
    def add_reaction(self, channel: str, name: str, timestamp: str):
        pass

    @abstractmethod
    def remove_reaction(self, channel: str, name: str, timestamp: str):
        pass

    @abstractmethod
    def get_message(self, channel: str, timestamp: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_channel_history(self, channel: str, latest: Optional[str] = None, inclusive: bool = False, limit: int = 1) -> List[Dict[str, Any]]:
        pass


class SlackPlatform(ChatPlatform):
    def __init__(self, slack_bot_token: str):
        self.slack_app = App(token=slack_bot_token)

    def send_message(self, channel: str, text: str, thread_ts: Optional[str] = None):
        self.slack_app.client.chat_postMessage(channel=channel, text=text, thread_ts=thread_ts)

    def add_reaction(self, channel: str, name: str, timestamp: str):
        self.slack_app.client.reactions_add(channel=channel, name=name, timestamp=timestamp)

    def remove_reaction(self, channel: str, name: str, timestamp: str):
        self.slack_app.client.reactions_remove(channel=channel, name=name, timestamp=timestamp)

    def get_message(self, channel: str, timestamp: str) -> Dict[str, Any]:
        result = self.slack_app.client.conversations_history(
            channel=channel,
            latest=timestamp,
            inclusive=True,
            limit=1
        )
        return result["messages"][0]

    def get_channel_history(self, channel: str, latest: Optional[str] = None, inclusive: bool = False, limit: int = 1) -> List[Dict[str, Any]]:
        result = self.slack_app.client.conversations_history(
            channel=channel,
            latest=latest,
            inclusive=inclusive,
            limit=limit
        )
        return result["messages"]



