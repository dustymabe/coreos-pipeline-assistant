from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from slack_bolt import App
import os
import logging

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

    def remove_reaction(self, channel: str, name: name, timestamp: str):
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


class MatrixPlatform(ChatPlatform):
    def __init__(self, homeserver_url: str, access_token: str):
        self.homeserver_url = homeserver_url
        self.access_token = access_token
        # TODO: Initialize Matrix client here

    def send_message(self, channel: str, text: str, thread_ts: Optional[str] = None):
        try:
            # TODO: Implement Matrix send_message
            print(f"Matrix: Sending message to {channel}: {text} (thread_ts: {thread_ts})")
        except Exception as e:
            logging.exception("Error sending Matrix message:")
        pass

    def add_reaction(self, channel: str, name: str, timestamp: str):
        try:
            # TODO: Implement Matrix add_reaction
            print(f"Matrix: Adding reaction {name} to {channel} at {timestamp}")
        except Exception as e:
            logging.exception("Error adding Matrix reaction:")
        pass

    def remove_reaction(self, channel: str, name: str, timestamp: str):
        try:
            # TODO: Implement Matrix remove_reaction
            print(f"Matrix: Removing reaction {name} from {channel} at {timestamp}")
        except Exception as e:
            logging.exception("Error removing Matrix reaction:")
        pass

    def get_message(self, channel: str, timestamp: str) -> Dict[str, Any]:
        try:
            # TODO: Implement Matrix get_message
            print(f"Matrix: Getting message from {channel} at {timestamp}")
            return {}
        except Exception as e:
            logging.exception("Error getting Matrix message:")
            return {}

    def get_channel_history(self, channel: str, latest: Optional[str] = None, inclusive: bool = False, limit: int = 1) -> List[Dict[str, Any]]:
        try:
            # TODO: Implement Matrix get_channel_history
            print(f"Matrix: Getting channel history for {channel} (latest: {latest}, inclusive: {inclusive}, limit: {limit})")
            return []
        except Exception as e:
            logging.exception("Error getting Matrix channel history:")
            return []
