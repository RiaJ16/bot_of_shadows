import requests
import json
import configparser as cfg


class BotOfShadows:

    def __init__(self, config):
        self.token = self.read_token_from_config_file(config)
        self.base = f"https://api.telegram.org/bot{self.token}/"

    def get_updates(self, offset=None):
        url = self.base + "getUpdates?timeout=100"
        if offset:
            url = url + f"&offset={offset+1}"
        r = requests.get(url)
        return json.loads(r.content)

    def send_message(self, msg, chat_id, topic=None):
        url = self.base + f"sendMessage?chat_id={chat_id}&text={msg}&parse_mode=html"
        if topic:
            url = url + f"&reply_to_message_id={topic}"
        if msg is not None:
            requests.get(url)

    @staticmethod
    def read_token_from_config_file(config, value='token'):
        parser = cfg.ConfigParser()
        parser.read(config)
        return parser.get('creds', value)
