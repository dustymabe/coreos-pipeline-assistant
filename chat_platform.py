from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from slack_bolt import App
import os
import logging
from nio import AsyncClient, MatrixRoom, RoomMessage, ClientConfig
from nio.store.database import SqliteStore
import asyncio # Import asyncio
import pprint
import time

class ChatPlatform(ABC):
    @abstractmethod
    def send_message(self, channel: str, text: str, thread_id: Optional[str] = None):
        pass

   #@abstractmethod
    def add_reaction(self, channel: str, name: str, timestamp: str):
        pass

   #@abstractmethod
    def remove_reaction(self, channel: str, name: str, timestamp: str):
        pass

    @abstractmethod
    def get_message(self, channel: str, timestamp: str) -> str:
        pass

    #@abstractmethod
    def get_channel_history(self, channel: str, latest: Optional[str] = None, inclusive: bool = False, limit: int = 1) -> List[Dict[str, Any]]:
        pass


class SlackPlatform(ChatPlatform):
    def __init__(self, slack_bot_token: str):
        self.slack_app = App(token=slack_bot_token)

    def send_message(self, channel: str, text: str, thread_id: Optional[str] = None):
        self.slack_app.client.chat_postMessage(channel=channel, text=text, thread_ts=thread_id)

    def add_reaction(self, channel: str, name: str, timestamp: str):
        self.slack_app.client.reactions_add(channel=channel, name=name, timestamp=timestamp)

    def remove_reaction(self, channel: str, name: str, timestamp: str):
        self.slack_app.client.reactions_remove(channel=channel, name=name, timestamp=timestamp)

   #def get_message(self, channel: str, timestamp: str) -> Dict[str, Any]:
   #    result = self.slack_app.client.conversations_history(
   #        channel=channel,
   #        latest=timestamp,
   #        inclusive=True,
   #        limit=1
   #    )
   #    return result["messages"][0]

    def get_channel_history(self, channel: str, latest: Optional[str] = None, inclusive: bool = False, limit: int = 1) -> List[Dict[str, Any]]:
        result = self.slack_app.client.conversations_history(
            channel=channel,
            latest=latest,
            inclusive=inclusive,
            limit=limit
        )
        return result["messages"]


class MatrixPlatform(ChatPlatform):
    def __init__(self, homeserver_url: str, access_token: str,
            matrix_room: str, process_message_func):
        self.starttime = int(time.time() * 1000) # current time in milliseconds
        self.homeserver_url = homeserver_url
        self.client = AsyncClient(
            homeserver=homeserver_url,
  #         user="@dustybot:matrix.org",
  #         device_id='tmp-coreos-pipeline-assistant',
            store_path="my_matrix_store",
            config=ClientConfig(
                store_sync_tokens=True,
                store=SqliteStore
            )
        )
        self.client.access_token = access_token
#       asyncio.run(self.client.login(token=access_token))
        asyncio.run(self.client.whoami()) # updates user_id device_id
        self.client.user = self.client.user_id
#       self.client.user_id = self.client.user
       #asyncio.run(self.client.sync(full_state=True))
        self.matrix_room = matrix_room
        self.process_message_func = process_message_func
        response = asyncio.run(self.client.room_resolve_alias(self.matrix_room))
       #pprint.pprint(response)
        self.matrix_room_id = response.room_id
        self.current_threadroot_message = None
        self.client.load_store()

    def send_message(self, channel: str, text: str, thread_id: Optional[str] = None):
        print(f"XXX: send_message channel: {channel}")
        print(f"XXX: send_message thread_id: {thread_id}")
        print(f"XXX: send_message text: {text}")
        try:
            content={
                "msgtype": "m.text",
                "body": text
            }
            if thread_id:
                content["m.relates_to"] = {
                    "rel_type": "m.thread",
                    "event_id": thread_id
                }
            response = asyncio.run(self.client.room_send(
                room_id=channel,
                message_type="m.room.message",
                content=content
            ))
            print(f"XXX: send_message response: {response}")
        except Exception as e:
            logging.exception("Error sending Matrix message:")

    def monitor_messages(self, room: MatrixRoom, event: RoomMessage):
        try:
            if room.room_id != self.matrix_room_id \
                or event.sender == self.client.user_id \
                or event.server_timestamp < self.starttime:
                # Don't process messages that:
                #   - is not in the matrix room we are moniotring
                #   - is a message sent by this bot itself
                #   - originated before this program started
                #       - we don't want to process entire history each
                #         time we start up
                return
            logging.info(f"XXX got message from {room.display_name}: {event.body}")
            pprint.pprint(event)
            logging.info(f"XXX {event}")
            is_threaded = False
            thread_id = None
            if self.client.user in \
                event.source.get('content', {}).get("m.mentions", {}).get("user_ids", []): 
                related = event.source.get('content', {}).get('m.relates_to', {})
                if related.get('rel_type', "") == 'm.thread':
                    is_threaded = True
                    thread_id = related["event_id"]
            if not is_threaded:
                return

            self.current_threadroot_message = self.get_message(channel=self.matrix_room, thread_id=thread_id)
                    
            result = self.process_message_func(
                room.display_name,
                thread_id or event.event_id,
                is_threaded,
                event.body
            )
            logging.info(f"Result from AI: {result}")
            self.send_message(text=result.output, channel=room.room_id, thread_id=thread_id)

        except Exception as e:
            logging.exception("Error sending Matrix message:")

    def get_message(self, channel: str, thread_id: str) -> str:
        try:
            # Get a specific message by it's matrix event ID, which
            # we've indexed as the thread_id in this program and passed
            # into this function.
            print(f"Matrix: Getting message from {channel} with thread_id: {thread_id}")
            response = asyncio.run(self.client.room_get_event(
                self.matrix_room_id,
                event_id=thread_id
            ))
            return response.event.body
        except Exception as e:
            logging.exception("Error getting Matrix message:")
            return {}


# XXX: get_channel_history not really needed for matrix IIUC
####def get_channel_history(self, channel: str, latest: Optional[str] = None, inclusive: bool = False, limit: int = 1) -> List[Dict[str, Any]]:
####    try:
####        # Getting channel history involves syncing and processing events.
####        # This is a complex operation with matrix_nio and is outside the scope of simple placeholders.
####        # For now, return an empty list as a placeholder.
####        print(f"Matrix: Getting channel history for {channel} (latest: {latest}, inclusive: {inclusive}, limit: {limit})")
####        return []
####    except Exception as e:
####        logging.exception("Error getting Matrix channel history:")
####        return []
