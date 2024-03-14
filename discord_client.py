"""Discord connect and info module"""
import requests

import fun


class DiscordClient:
    def __init__(self, auth_token: str):
        self.api_point = "https://discord.com/api/v9/"
        self.headers = {"Authorization": auth_token}

    def fetch_messages(self, channel_id: int, message_limit: int = 10) -> list:
        response = requests.get(f'{self.api_point}/channels/{channel_id}/messages?limit={message_limit}',
                                headers=self.headers)
        if response.ok:
            return response.json()
        elif response.status_code == 401:
            fun.error(f'this AccessToken does not have the nessasary scope.')
        elif response.status_code == 429:
            fun.error(f'You are being Rate Limited. Retry after')
        else:
            fun.error(f'Unexpected HTTP {response.status_code}')
