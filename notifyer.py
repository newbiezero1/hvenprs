"""Module for notifying via TelegramBot about all process"""
import requests

import config


class Notifyer:
    """Class for notifying via TelegramBot"""
    def __init__(self, chat_id: int):
        self.token = config.tg_api_key
        self.chat_id = chat_id

    def send_message(self, message: str, silence: bool = False, markdown: bool = True) -> None:
        disable_notification = ""
        if silence:
            disable_notification = "&disable_notification=true"
        parse_mode = "parse_mode=markdown&"
        if not markdown:
            parse_mode = ""
        url = f'https://api.telegram.org/bot{self.token}/sendMessage?{parse_mode}chat_id={self.chat_id}{disable_notification}'
        requests.post(url, data={"text": message})  # this sends the message

    def new_trade(self, trade_info: dict, origin_message: dict) -> None:
        message = f'''Parse trade: 
            PAIR: *{trade_info["pair"]}*
            SIDE: *{trade_info["side"]}*
            ENTRY: *{trade_info["entry"]}*
            SL: *{trade_info["sl"]}*
            TP: *{trade_info["tp"]}*
            ===
            Original message:
            {origin_message["content"]}'''.replace("    ", "")
        if origin_message['attachments']:
            message += f'''\n{origin_message['attachments'][0]['url']}'''
        self.send_message(message, silence=True, markdown=False)

    def new_alert(self, alert_info: dict, origin_message: str) -> None:
        message = f'''Parse alert: 
            PAIR: *{alert_info["pair"]}*
            ACTION: *{alert_info["action"]}*
            VALUE: *{alert_info["value"]}*
            ===
            Original message:
            {origin_message}'''.replace("    ", "")
        self.send_message(message, silence=True)

    def alert_report(self, report: str) -> None:
        message = f'''*Alert Report*\n{report}'''
        self.send_message(message, silence=True)

    def place_order(self, order: dict) -> None:
        if not order["price"]:
            order["price"] = "market"
        message = f'''Send order: 
                    PAIR: *{order["symbol"]}*
                    SIDE: *{order["side"]}*
                    TYPE: *{order["orderType"]}*
                    ENTRY: *{order["price"]}*
                    QTY: *{order["qty"]}*
                    SL: *{order["stopLoss"]}*
                    TP: *{order["takeProfit"]}*
                    ===
                    Current price: *{order["current_price"]}*
                    Result: *{order["result"]}*'''.replace("    ", "")
        self.send_message(message, silence=True)

    def lost_sl(self, trade_info: dict, origin_message: str) -> None:
        message = f'''Parse trade without SL and saved: 
            PAIR: *{trade_info["pair"]}*
            SIDE: *{trade_info["side"]}*
            ENTRY: *{trade_info["entry"]}*
            ===
            Original message:
            {origin_message}'''.replace("    ", "")
        self.send_message(message, silence=True)

    def broken_message(self, message: str) -> None:
        message = f'''*Can't parse message:*\n {message}'''
        self.send_message(message)

    def send_error(self, message: str) -> None:
        message = f'''*ERROR:*\n {message}'''
        self.send_message(message, markdown=False)
