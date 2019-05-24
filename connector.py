import logging
from typing import Text
import requests
import json

from flask import Blueprint, request, jsonify, make_response

from rasa_core.channels.channel import UserMessage, OutputChannel, InputChannel

from rasa_core.channels.rocketchat import RocketChatBot
from rocketchat_py_sdk.driver import Driver
from rocketchat_API.rocketchat import RocketChat

logger = logging.getLogger(__name__)


class RocketChatInput(InputChannel):
    """RocketChat input channel implementation."""

    on_new_message = None

    @classmethod
    def name(cls):
        return "rocketchat"

    @classmethod
    def from_credentials(cls, credentials):
        if not credentials:
            cls.raise_missing_credentials_exception()

        return cls(credentials.get("user"),
                   credentials.get("password"),
                   credentials.get("server_url"))

    def __init__(self, user: Text, password: Text, server_url: Text) -> None:

        self.user = user
        self.password = password
        self.server_url = server_url

        self.socket_url = server_url.replace(
            "http://", '').replace("https://", '')

        logger.info("[+] Connecting to Rocketchat socket...")
        self.driver = Driver(self.socket_url, ssl=False)
        self.driver.connect()

        logger.info("[+] Logging in to Rocketchat...")
        self.driver.login(user, password)

        logger.info("[+] Subscribing to messages...")
        self.driver.subscribe_to_messages()
        self.driver.add_prefix_handler('', self.send_from_data)

        self.output_channel = RocketChatBot(
            self.user,
            self.password,
            self.server_url
        )

        self.config = Config()

    def send_from_data(self, driver, data):

        response = self.output_channel.rocket.rooms_info(room_id=data['rid'])
        room = json.loads(response.text)

        # Ignore bot's own messages
        if data['u']['username'] == self.user:
            return

        # Ignore DMs unless configured not to
        isDM = room['room']['t'] == 'd'
        if isDM and not self.config.respond_to_dm:
            return

        # Ignore Livechat unless configured not to
        isLC = room['room']['t'] == 'l'
        if isLC and not self.config.respond_to_livechat:
            return

        # Ignore messages in un-joined public rooms
        # unless configured not to
        # Note: this wont work with live transfer
        if (
            not (isDM or isLC)
            and self.user not in room['room']['usernames']
            and not self.config.listen_all_public
        ):
            return

        if self.on_new_message is None:
            logger.warning("[+] Waiting for server...")

            import time
            while self.on_new_message is None:
                # waiting resource from other thread
                time.sleep(1)

        self.send_message(
            data['msg'],
            data['u']['username'],
            data['rid'],
            self.on_new_message
        )

    def send_message(self, text, sender_name, recipient_id, on_new_message):
        if sender_name != self.user:
            user_msg = UserMessage(
                text,
                self.output_channel,
                recipient_id,
                input_channel=self.name()
            )

            on_new_message(user_msg)

    def blueprint(self, on_new_message):
        self.on_new_message = on_new_message

        rocketchat_webhook = Blueprint('rocketchat_webhook', __name__)
        @rocketchat_webhook.route("/", methods=['GET'])
        def health():
            return jsonify({"status": "ok"})

        return rocketchat_webhook


class Config:

    def __init__(self):
        from os import getenv

        self.listen_all_public = getenv('LISTEN_ON_ALL_PUBLIC', False)
        self.respond_to_livechat = getenv('RESPOND_TO_LIVECHAT', False)
        self.respond_to_dm = getenv('RESPOND_TO_DM', False)
        self.respond_to_edited = getenv('RESPOND_TO_EDITED', False)
