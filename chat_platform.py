from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from slack_bolt import App
import os
import logging
from nio import AsyncClient
import asyncio # Import asyncio

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


class MatrixPlatform(ChatPlatform):
    def __init__(self, homeserver_url: str, access_token: str):
        self.homeserver_url = homeserver_url
        self.access_token = access_token
        self.client = AsyncClient(homeserver_url, access_token)

    async def send_message(self, channel: str, text: str, thread_ts: Optional[str] = None):
        try:
            # Matrix doesn't have direct thread_ts like Slack, typically replies are used
            # For now, we'll just send a regular message
            response = await self.client.room_send(
                room_id=channel,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": text,
                },
            )
            # TODO: Handle response (e.g., check for errors)
        except Exception as e:
            logging.exception("Error sending Matrix message:")

    async def add_reaction(self, channel: str, name: str, timestamp: str):
        try:
            # In Matrix, reactions are typically applied to event IDs, not timestamps
            # We'll need to figure out the event ID from the timestamp, which is complex.
            # For now, just a placeholder
            print(f"Matrix: Adding reaction {name} to {channel} at {timestamp}")
        except Exception as e:
            logging.exception("Error adding Matrix reaction:")

    async def remove_reaction(self, channel: str, name: str, timestamp: str):
        try:
            # Similar to add_reaction, requires event ID
            print(f"Matrix: Removing reaction {name} from {channel} at {timestamp}")
        except Exception as e:
            logging.exception("Error removing Matrix reaction:")

    async def get_message(self, channel: str, timestamp: str) -> Dict[str, Any]:
        try:
            # Getting a specific message by timestamp is not straightforward in Matrix via client.sync()
            # It would involve iterating through historical events or using a dedicated API if available.
            # For now, return an empty dict as a placeholder.
            print(f"Matrix: Getting message from {channel} at {timestamp}")
            return {}
        except Exception as e:
            logging.exception("Error getting Matrix message:")
            return {}

    async def get_channel_history(self, channel: str, latest: Optional[str] = None, inclusive: bool = False, limit: int = 1) -> List[Dict[str, Any]]:
        try:
            # Getting channel history involves syncing and processing events.
            # This is a complex operation with matrix_nio and is outside the scope of simple placeholders.
            # For now, return an empty list as a placeholder.
            print(f"Matrix: Getting channel history for {channel} (latest: {latest}, inclusive: {inclusive}, limit: {limit})")
            return []
        except Exception as e:
            logging.exception("Error getting Matrix channel history:")
            return []
