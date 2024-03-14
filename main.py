import json

import config
from discord_client import DiscordClient
import fun
from notifyer import Notifyer
from bybit import Bybit
from ub import UbParser


def check_trades(trader: str):
    """Check new trades and make trade"""
    all_messages = client.fetch_messages(config.traders_channels[trader])
    new_message = fun.check_new_message(all_messages, config.files_list[trader])
    if new_message['content']:
        if trader == 'ub':
            parser = UbParser()
        else:
            return
        parser.parse_trade_message_data(new_message['content'])
        for user in config.users.values():
            notifyer = Notifyer(user["tg_chat_id"])

            if parser.check_trade_data():
                # check sl in trade
                if not parser.trade["sl"]:
                    notifyer.lost_sl(parser.trade, new_message['content'])
                    continue
                # notify in tg about new message
                notifyer.new_trade(parser.trade, new_message)
                # make trade if this user enable autotrade
                if user["autotrade_enabled"]:
                    try:
                        bybit = Bybit(user)
                    except Exception as e:
                        fun.error(f'can\'t connect to bybit api, user: *{user["name"]}*', finish=False)
                        continue
                    bybit.set_trade_data(parser.trade)
                    bybit.make_trade()
                    if bybit.api_error_flag:
                        fun.error(f'Error: {bybit.api_error_msg}', finish=False)
                        continue
                    for order in bybit.orders:
                        notifyer.place_order(order)
            else:
                notifyer.broken_message(new_message['content'])


client = DiscordClient(config.discord_token)
# trade section
check_trades('ub')
