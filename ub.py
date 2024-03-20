"""Parser ub message"""


class UbParser:
    def __init__(self):
        self.trade = {
            'pair': '',
            'side': '',
            'entry': [],
            'sl': '',
            'tp1': '',
            'tp2': '',
            'tp': '',
            'risk': 1.0,
        }
        self.alert = {
            'pair': '',
            'action': '',
            'value': '',
        }
        self.alert_action_ignore = ['filled', 'stopped', 'update']
        self.alert_action = ['move_sl', 'close', 'cancel', 'change_sl']
        return

    def format_pair(self, pair: str) -> str:
        if pair.find('1000') >= 0:
            pair = pair.replace('1000','')
            pair = pair + '1000'
            return pair
        return pair

    def find_pair(self, line: str) -> None:
        """find pair in line and save to data"""
        """example: **ETH/SPOT - LONG**"""
        """example: RNDR - Long (0.5R)"""
        if line.lower().find("spot") > 0 or line.lower().find("perp") > 0:
            data = line.split("/")
            self.trade["pair"] = self.format_pair(data[0].replace('*', '').lower())
            return
        if line.lower().find('- long') >= 0:
            data = line.split(" ")
            self.trade["pair"] = self.format_pair(data[0].lower())

    def find_side(self, line: str) -> None:
        """find side in line and save to data"""
        """example: **ETH/SPOT - LONG**"""
        if line.lower().find("long") > 0:
            self.trade["side"] = "long"
        elif line.lower().find("short") > 0:
            self.trade["side"] = "short"
        elif line.lower().find("limit") > 0:
            # recognize by potential sl level
            if line.lower().find("close below"):
                self.trade["side"] = "long"

    def format_entry(self, entry: str) -> list:
        """format list entry point"""
        if entry.find("/") >= 0:
            return entry.split("/")
        if entry.find(" - ") >= 0:
            return entry.split(" - ")
        if entry.find(" -") >= 0:
            return entry.split(" -")
        if entry == 'cmp':
            return ['cmp']
        return [entry]

    def find_entry(self, line: str) -> None:
        """find entry point in line and save to data"""
        """example: Entry:2052.32"""
        if line.lower().find("entry:") >= 0:
            data = line.lower().split("entry:")
            self.trade["entry"] = self.format_entry(data[1].strip())
            return

    def find_sl(self, line: str) -> None:
        """find sl point in line and save to data"""
        """example: SL: 1903.99 | SSL: H1 1.393"""
        if line.lower().find("invalidation:") >= 0:
            data = line.lower().split("invalidation:")
            self.trade["sl"] = data[1].strip()
            return

    def find_tp(self, line: str) -> None:
        """find tp point in line and save to data"""
        """example: TP: 2415.2"""
        if line.lower().find("tp1") >= 0:
            data = line.lower().split("tp1:")
            self.trade["tp1"] = data[1].split(' ')[0].strip()
            return
        if line.lower().find("tp2") >= 0:
            data = line.lower().split("tp2:")
            self.trade["tp2"] = data[1].split(' ')[0].strip()
            return
        if line.lower().find("tp3") >= 0:
            data = line.lower().split("tp3:")
            if data[1].strip().lower().find('tbd') >=0:
                return
            self.trade["tp"] = data[1].split(' ')[0].strip()
            return

    def find_in_many_line(self, lines: list) -> None:
        """find any needes in many line and save to data"""
        """ message example
                **ETH/SPOT - LONG**
                Entry: 2052.32/1985.78
                SL: 1903.99
                TP: 2415.2
                <@&1202381806989754378>"""
        for line in lines:
            if not self.trade['pair']:
                self.find_pair(line)
            if not self.trade['side']:
                self.find_side(line)
            if not self.trade['entry']:
                self.find_entry(line)
            if not self.trade['sl']:
                self.find_sl(line)
            if not self.trade['tp1']:
                self.find_tp(line)
            if not self.trade['tp2']:
                self.find_tp(line)
            if not self.trade['tp']:
                self.find_tp(line)

        if not self.trade['tp']:
            for line in lines:
                if line.lower().find("tp2") >= 0:
                    data = line.lower().split("tp2:")
                    self.trade["tp"] = data[1].split(' ')[0].strip()

    def parse_trade_message_data(self, message: str) -> dict:
        """parse ub message"""
        message = message.replace('~','').replace('$','').replace(' .','')
        message = message.replace(': ',':')
        lines = message.split("\n")
        print(lines)
        self.find_in_many_line(lines)

        return self.trade

    def check_trade_data(self) -> bool:
        """"Check all required params"""
        if not self.trade['pair']:
            return False
        if not self.trade['side']:
            return False
        if not self.trade['entry']:
            return False
        if not self.trade['sl']:
            return False
        return True
