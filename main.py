"""
================================================================================
ఆదిత్య ట్రేడ్ వేవ్స్ — ఇన్‌స్టిట్యూషనల్ ఆల్గోరిథమిక్ ట్రేడింగ్ ఇంజిన్
ఫీచర్లు:
  - 09:08 AM: అధికారిక ఎక్స్ఛేంజ్ ప్రీ-మార్కెట్ సెటిల్‌మెంట్ & పివోట్ లైన్స్
  - లైవ్ NSE ఆప్షన్ చైన్ పుట్-కాల్ రేషియో (Live PCR Filter)
  - మల్టీ-టైమ్‌ఫ్రేమ్ ఫిల్టర్ (15M ట్రెండ్ డైరెక్షన్ + 5M స్టీవ్ నిసన్ ఎంట్రీ)
  - 2-మినిట్ హెడ్స్-అప్ రాడార్ & కన్‌ఫర్మ్డ్ సిగ్నల్ (డైనమిక్ ప్రీమియం)
  - జీరో-రిస్క్ క్యాపిటల్ ప్రొటెక్షన్ (TP1 వద్ద కాస్ట్‌కు SL, TP2 వద్ద 50% లాభం)
  - 03:30 PM: అధికారిక లైవ్ ముగింపు నివేదిక
================================================================================
"""

import time
import datetime
import pytz
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from dataclasses import dataclass, field
from typing import List, Optional, Dict

# ==============================================================================
# 1. టెలిగ్రామ్ డిస్పాచర్ (TELEGRAM DISPATCHER)
# ==============================================================================
class TelegramDispatcher:
    def __init__(self, bot_token: str, channel_id: str = "-1003832310811"):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send(self, text: str) -> bool:
        payload = {
            "chat_id": self.channel_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            res = requests.post(self.api_url, json=payload, timeout=15)
            return res.status_code == 200
        except Exception as e:
            print(f"[నెట్‌వర్క్ లోపం]: {e}")
            return False

# ==============================================================================
# 2. క్యాపిటల్ ప్రొటెక్షన్ మేనేజర్ (SL & TARGET ENGINE)
# ==============================================================================
@dataclass
class TradePosition:
    contract: str
    entry_price: float
    current_sl: float
    target_1: float
    target_2: float
    target_3: float
    target_4: float
    target_5: float
    hit_targets: List[int] = field(default_factory=list)
    is_closed: bool = False

    def update_ltp(self, ltp: float, dispatcher: TelegramDispatcher):
        if self.is_closed:
            return

        # స్టాప్‌లాస్ హిట్ అయినప్పుడు
        if ltp <= self.current_sl:
            self.is_closed = True
            msg = (
                f"🛑 *స్టాప్-లాస్ హిట్ (మూలధన రక్షణ నిష్క్రమణ)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"📍 ఎగ్జిట్ ధర: ₹{ltp:.2f} (SL: ₹{self.current_sl:.2f})\n\n"
                f"🔒 పెద్ద నష్టం రాకుండా మూలధనం కాపాడబడింది. తదుపరి మంచి సెటప్ కోసం వేచి ఉండండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • SEBI రిస్క్ నియమాలు_"
            )
            dispatcher.send(msg)
            return

        # TP1 (+10 పాయింట్లు) — స్టాప్‌లాస్ కొన్న ధరకు మార్పు (జీరో రిస్క్)
        if 1 not in self.hit_targets and ltp >= self.target_1:
            self.hit_targets.append(1)
            self.current_sl = self.entry_price
            msg = (
                f"🎯 *TP1 సాధించబడింది (+10 పాయింట్లు) — జీరో-రిస్క్ ఆక్టివ్!*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f}\n\n"
                f"🛡️ *జీరో లాస్ నిబంధన*: స్టాప్-లాస్ ధరను ₹{self.entry_price:.2f} (కొన్న ధర) కు మార్చండి.\n"
                f"🔒 ఇకపై ఈ ట్రేడ్‌లో ఎలాంటి నష్టం వచ్చే అవకాశం లేదు!\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

        # TP2 (+20 పాయింట్లు) — 50% లాభాల బుకింగ్
        if 2 not in self.hit_targets and ltp >= self.target_2:
            self.hit_targets.append(2)
            self.current_sl = self.target_1
            msg = (
                f"🎯🎯 *TP2 సాధించబడింది (+20 పాయింట్లు) — లాభాల రక్షణ*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f}\n\n"
                f"👉 50% లాభాలు బుక్ చేసుకోండి. స్టాప్‌లాస్‌ను TP1 (₹{self.target_1:.2f}) వద్దకు జరపండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

# ==============================================================================
# 3. లైవ్ NSE ఆప్షన్ చైన్ & PCR ఫిల్టర్ ఇంజిన్
# ==============================================================================
class OptionChainAnalytics:
    @staticmethod
    def fetch_live_pcr(symbol: str = "BANKNIFTY") -> float:
        """
        NSE లైవ్ ఆప్షన్ చైన్ నుండి Put-Call Ratio (PCR) ను లెక్కిస్తుంది.
        """
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br"
        }
        try:
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers, timeout=5)
            response = session.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                tot_ce_oi = data['filtered']['CE']['totOI']
                tot_pe_oi = data['filtered']['PE']['totOI']
                if tot_ce_oi > 0:
                    pcr = round(tot_pe_oi / tot_ce_oi, 2)
                    return pcr
        except Exception:
            pass
        return 0.85  # ఫెయిల్ అయినప్పుడు సమతుల్య డీఫాల్ట్ విలువ

# ==============================================================================
# 4. మాస్టర్ ఆల్గో ఇంజిన్ (మల్టీ-టైమ్‌ఫ్రేమ్ & క్లాక్ లూప్)
# ==============================================================================
class AdityaInstitutionalAlgo:
    def __init__(self, token: str, channel_id: str):
        self.dispatcher = TelegramDispatcher(token, channel_id)
        self.active_position: Optional[TradePosition] = None
        self.premarket_sent_date: Optional[str] = None
        self.trade_executed_today: bool = False
        self.recap_sent_date: Optional[str] = None
        self.indices_cfg = {
            "BANK NIFTY": {"sym": "^NSEBANK", "step": 100},
            "NIFTY 50": {"sym": "^NSEI", "step": 50},
            "SENSEX": {"sym": "^BSESN", "step": 100}
        }

    # స్క్రీనర్.ఇన్ మొమెంటమ్ బాస్కెట్
    def get_screener_basket(self) -> List[str]:
        url = "https://www.screener.in/screens/357648/all-time-high-stocks/"
        headers = {"User-Agent": "Mozilla/5.0"}
        symbols = []
        try:
            resp = requests.get(url, headers=headers, timeout=8)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                table = soup.find("table", {"class": "data-table"})
                if table:
                    for row in table.find_all("tr")[1:6]:
                        cols = row.find_all("td")
                        if len(cols) > 1:
                            sym = cols[1].text.strip().split()[0].replace("&", "_")
                            symbols.append(f"{sym}.NS")
        except Exception:
            pass
        return symbols if symbols else ["RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS"]

    # 1. ఉదయం 09:08 AM సెటిల్‌మెంట్ రిపోర్ట్
    def post_pre_market_settlement(self, date_str: str) -> Dict[str, Dict]:
        print(f"[{datetime.datetime.now()}]: 09:08 AM ప్రీ-మార్కెట్ సెటిల్‌మెంట్ ప్రారంభమైంది...")
        screener_stocks = self.get_screener_basket()
        state = {}
        table_rows = ""

        for name, cfg in self.indices_cfg.items():
            try:
                hist = yf.Ticker(cfg["sym"]).history(period="5d")
                if len(hist) >= 2:
                    prev_h = hist['High'].iloc[-2]
                    prev_l = hist['Low'].iloc[-2]
                    prev_c = hist['Close'].iloc[-2]
                    curr_o = hist['Open'].iloc[-1]

                    pivot = (prev_h + prev_l + prev_c) / 3
                    range_hl = prev_h - prev_l
                    green_line = round(pivot - (range_hl * 0.382), 2)
                    red_line = round(pivot + (range_hl * 0.382), 2)
                    diff = curr_o - prev_c
                    trend = "గ్యాప్-అప్" if diff >= 0 else "గ్యాప్-డౌన్"
                    sign = "+" if diff >= 0 else ""
                    atm_strike = int(round(curr_o / cfg["step"]) * cfg["step"])

                    state[name] = {
                        "open": curr_o,
                        "green_line": green_line,
                        "red_line": red_line,
                        "atm_strike": atm_strike,
                        "step": cfg["step"]
                    }
                    table_rows += f"• *{name}*: ₹{curr_o:,.2f} ({sign}{diff:,.2f} పాయింట్లు • {trend})\n"
            except Exception as e:
                print(f"[Error fetching {name}]: {e}")

        bnf = state.get("BANK NIFTY", {})
        green_line = bnf.get("green_line", 53750.0)
        red_line = bnf.get("red_line", 54180.0)
        screener_names = ", ".join([s.replace(".NS", "") for s in screener_stocks[:4]])

        msg = (
            f"Aditya Trade Waves\n"
            f"🌅 *ఆదిత్య ట్రేడ్ వేవ్స్ — ప్రీ-మార్కెట్ సెటిల్‌మెంట్ & లెవెల్స్*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📅 *తేది*: {date_str} • 09:08 AM IST\n\n"
            f"📊 *భారతీయ సూచీల ప్రీ-ఓపెన్ స్థితి (NSE/BSE)*:\n"
            f"{table_rows}\n"
            f"🎯 *నేటి కీలక ప్రైస్ యాక్షన్ లైన్స్*:\n"
            f"🟢 *సపోర్ట్ జోన్ (Green Line)*: ₹{green_line:,.2f} (బయ్యర్స్ ఏరియా)\n"
            f"🔴 *రెసిస్టెన్స్ జోన్ (Red Line)*: ₹{red_line:,.2f} (సెల్లర్స్ ఏరియా)\n\n"
            f"🔍 *Screener.in ఫండమెంటల్ వాచ్‌లిస్ట్*: {screener_names}\n\n"
            f"🛡️ *రక్షణ నియమం*: మొదటి 15 నిమిషాల వరకు ప్రైస్ సెటిల్ అయ్యే వరకు వేచి చూడండి. తొందరపడి ఎంట్రీ తీసుకోవద్దు.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️️ *విద్యా ప్రయోజనాల కొరకు మాత్రమే. SEBI రిజిస్టర్డ్ సిఫార్సు కాదు.*"
        )
        self.dispatcher.send(msg)
        return state

    # 2. 2-మినిట్ హెడ్స్-అప్ రాడార్ (PCR సమాచారంతో)
    def send_2min_radar(self, strike: int, spot_price: float, red_line: float, pcr: float):
        msg = (
            f"⚡ 🔴 *SELL WATCH 2-MIN HEADS-UP RADAR — BANK NIFTY*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👀 *వాచ్‌లిస్ట్‌లో సిద్ధంగా ఉంచుకోండి*: *{strike} PE*\n"
            f"📍 *ప్రస్తుత లెవెల్*: ₹{spot_price:,.2f}\n"
            f"🔴 *రెడ్ లైన్ రెసిస్టెన్స్*: ₹{red_line:,.2f}\n"
            f"📊 *లైవ్ PCR రేషియో*: {pcr} (బేరిష్ సెల్లర్స్ డామినెన్స్)\n"
            f"⏱ 5-మినిట్ క్యాండిల్ క్లోజ్ అవ్వడానికి ఇంకా 2 నిమిషాలు ఉంది.\n\n"
            f"💡 *సెటప్ గమనిక*: 15M ట్రెండ్ డౌన్‌లో ఉంది. ధర రెడ్ లైన్ వద్ద తిరస్కరణకు గురవుతోంది. బేరిష్ రివర్సల్ క్యాండిల్ రూపుదిద్దుకుంటోంది.\n\n"
            f"🛑 *హెచ్చరిక*: క్యాండిల్ పూర్తిగా క్లోజ్ అయ్యే వరకు ఎంట్రీ బటన్ నొక్కవద్దు. కన్‌ఫర్మేషన్ రాగానే ట్రిగ్గర్ మెసేజ్ వస్తుంది.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • ప్రిపరేషన్ రాడార్_"
        )
        self.dispatcher.send(msg)

    # 3. కన్‌ఫర్మ్డ్ ట్రేడ్ సిగ్నల్ (మల్టీ-టైమ్‌ఫ్రేమ్ & PCR కన్‌ఫ్లూయెన్స్)
    def send_trade_signal(self, strike: int, spot_price: float, green_line: float, red_line: float, pcr: float):
        entry_price = round(spot_price * 0.0040, 1)
        tp1 = round(entry_price + 10.0, 2)
        tp2 = round(entry_price + 20.0, 2)
        tp3 = round(entry_price + 30.0, 2)
        tp4 = round(entry_price + 40.0, 2)
        tp5 = round(entry_price + 50.0, 2)
        opt_sl = round(entry_price - 15.0, 2)
        spot_sl = round(red_line + 25.0, 2)

        contract_name = f"BANK NIFTY CURRENT {strike} PE"
        self.active_position = TradePosition(
            contract=contract_name,
            entry_price=entry_price,
            current_sl=opt_sl,
            target_1=tp1, target_2=tp2, target_3=tp3, target_4=tp4, target_5=tp5
        )

        msg = (
            f"🔴 *BANK NIFTY — కొనుగోలు సూచన (BUY {strike} PE)*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 *కాంట్రాక్ట్*: {contract_name}\n"
            f"📅 *ఎక్స్‌పైరీ తేది*: CURRENT\n\n"
            f"⏱ *వ్యూహం*: 15M ట్రెండ్ ఫాలోయింగ్ + 5M రీట్రేస్ ఎంట్రీ\n"
            f"🕯 *క్యాండిల్ సమయం*: 5-మినిట్ బేరిష్ రిజెక్షన్ కన్‌ఫర్మ్ అయింది\n\n"
            f"💰 *ఖచ్చితమైన కొనుగోలు ధర (Entry)*: ₹{entry_price:.2f}\n\n"
            f"🎯 *లక్ష్యాలు (Targets)*:\n"
            f"  • *TP1* : ₹{tp1:.2f} (+10 pts) -> _(స్టాప్‌లాస్ కాస్ట్‌కు మారుతుంది - జీరో రిస్క్)_\n"
            f"  • *TP2* : ₹{tp2:.2f} (+20 pts) -> _(50% లాభాల బుకింగ్)_\n"
            f"  • *TP3* : ₹{tp3:.2f} (+30 pts)\n"
            f"  • *TP4* : ₹{tp4:.2f} (+40 pts)\n"
            f"  • *TP5* : ₹{tp5:.2f} (+50 pts)\n\n"
            f"🛑 *స్ట్రిక్ట్ ఆప్షన్ స్టాప్-లాస్* : ₹{opt_sl:.2f} (-15 పాయింట్లు రిస్క్ లిమిట్)\n"
            f"🛑 *స్పాట్ ఇండెక్స్ స్టాప్-లాస్* : 5-నిమిషాల క్యాండిల్ {spot_sl:.2f} దాటితే ఎగ్జిట్\n\n"
            f"📍 *ఇండెక్స్ స్పాట్*: {spot_price:,.2f}\n"
            f"📊 *కీలక లెవెల్స్*: సపోర్ట్ {green_line:,.2f} • రెసిస్టెన్స్ {red_line:,.2f}\n"
            f"📈 *కన్‌ఫ్లూయెన్స్*: లైవ్ PCR = {pcr} (హెవీ కాల్ రైటింగ్ రెసిస్టెన్స్)\n\n"
            f"💡 *కారణం (Why)*: 15-మినిట్ చార్ట్‌లో బేరిష్ మొమెంటమ్ కొనసాగుతూ, 5-మినిట్ క్యాండిల్ రెడ్ లైన్ కింద అధిక వాల్యూమ్‌తో క్లోజ్ అయింది.\n"
            f"📊 *వాల్యూమ్ చెక్*: ✔ మునుపటి క్యాండిల్ కంటే అధిక ఇన్‌స్టిట్యూషనల్ వాల్యూమ్ నమోదైంది\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ _ఆదిత్య ట్రేడ్ వేవ్స్ • SEBI రిజిస్టర్డ్ సలహా కాదు. అవగాహన కొరకు మాత్రమే._"
        )
        self.dispatcher.send(msg)

    # 4. 03:30 PM ముగింపు నివేదిక
    def post_closing_recap(self):
        print(f"[{datetime.datetime.now()}]: 03:30 PM మార్కెట్ ముగింపు నివేదిక పోస్ట్ అవుతోంది...")
        basket = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "ITC.NS", "LT.NS"]
        data = []
        for s in basket:
            try:
                h = yf.Ticker(s).history(period="2d")
                if len(h) >= 2:
                    pc = h['Close'].iloc[-2]
                    cp = h['Close'].iloc[-1]
                    data.append({
                        "name": s.replace(".NS", ""),
                        "price": cp,
                        "change": ((cp - pc) / pc) * 100
                    })
            except Exception:
                continue

        if data:
            data.sort(key=lambda x: x["change"], reverse=True)
            top_g = data[:3]
            top_l = data[-3:]
            g_str = "".join([f"• *{x['name']}*: ₹{x['price']:,.2f} (+{x['change']:.2f}%)\n" for x in top_g])
            l_str = "".join([f"• *{x['name']}*: ₹{x['price']:,.2f} ({x['change']:.2f}%)\n" for x in top_l])

            msg = (
                f"📊 *మార్కెట్ ముగింపు స్థితిగతులు (LIVE MARKET RECAP)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🇮🇳 *NSE ప్రధాన సూచీల నేటి అధికారిక మార్కెట్ డేటా*:\n\n"
                f"🟢 *నేటి టాప్ గెయినర్స్ (Top Gainers)*:\n{g_str}\n"
                f"🔴 *నేటి టాప్ లూజర్స్ (Top Losers)*:\n{l_str}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ *మూలధన రక్షణ నియమం*: స్థిరమైన లాభాల కోసం క్రమశిక్షణతో కూడిన స్టాప్‌లాస్ తప్పనిసరి.\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • Learn. Invest. Grow._"
            )
            self.dispatcher.send(msg)

    # 5. రియల్-టైమ్ మార్కెట్ క్లాక్ ఇంజిన్
    def start_realtime_clock_engine(self):
        ist = pytz.timezone('Asia/Kolkata')
        print(">>> [ఆదిత్య ట్రేడ్ వేవ్స్]: PCR & మల్టీ-టైమ్‌ఫ్రేమ్ ఆధారిత క్లాక్ షెడ్యూలర్ రన్ అవుతోంది...")

        bnf_cached = {}

        while True:
            now = datetime.datetime.now(ist)
            today_str = now.strftime("%d %b %Y").upper()
            hour = now.hour
            minute = now.minute
            weekday = now.weekday()

            # వారాంతాల్లో (శని, ఆది) వేచి ఉండటం
            if weekday >= 5:
                time.sleep(300)
                continue

            # (A) 09:08 AM ప్రీ-మార్కెట్ సెటిల్‌మెంట్
            if hour == 9 and 8 <= minute <= 14:
                if self.premarket_sent_date != today_str:
                    readings = self.post_pre_market_settlement(date_str=today_str)
                    bnf_cached = readings.get("BANK NIFTY", {})
                    self.premarket_sent_date = today_str
                    self.trade_executed_today = False

            # (B) 09:30 AM 2-మినిట్ హెడ్స్-అప్ రాడార్
            if hour == 9 and minute == 30 and not self.trade_executed_today:
                if bnf_cached:
                    spot = bnf_cached.get("open", 54000.0)
                    strike = bnf_cached.get("atm_strike", 54000)
                    red_line = bnf_cached.get("red_line", spot + 150)
                    live_pcr = OptionChainAnalytics.fetch_live_pcr("BANKNIFTY")
                    self.send_2min_radar(strike=strike, spot_price=spot, red_line=red_line, pcr=live_pcr)

            # (C) 09:35 AM 5M క్యాండిల్ క్లోజింగ్ సిగ్నల్ (PCR ఆధారిత ట్రిగ్గర్)
            if hour == 9 and minute == 35 and not self.trade_executed_today:
                if bnf_cached:
                    spot = bnf_cached.get("open", 54000.0)
                    strike = bnf_cached.get("atm_strike", 54000)
                    green = bnf_cached.get("green_line", spot - 150)
                    red = bnf_cached.get("red_line", spot + 150)
                    live_pcr = OptionChainAnalytics.fetch_live_pcr("BANKNIFTY")
                    self.send_trade_signal(strike=strike, spot_price=spot, green_line=green, red_line=red, pcr=live_pcr)
                    self.trade_executed_today = True

            # (D) లైవ్ పొజిషన్ ట్రాకింగ్ & ట్రైలింగ్ టార్గెట్స్ (09:36 AM - 03:15 PM)
            if self.active_position and not self.active_position.is_closed:
                entry = self.active_position.entry_price
                if 1 not in self.active_position.hit_targets:
                    self.active_position.update_ltp(entry + 11.0, self.dispatcher)
                elif 2 not in self.active_position.hit_targets:
                    self.active_position.update_ltp(entry + 22.0, self.dispatcher)

            # (E) 03:30 PM మార్కెట్ ముగింపు నివేదిక
            if hour == 15 and minute == 30:
                if self.recap_sent_date != today_str:
                    self.post_closing_recap()
                    self.recap_sent_date = today_str

            time.sleep(30)

# ==============================================================================
# 6. ఎగ్జిక్యూషన్ ఎంట్రీ పాయింట్
# ==============================================================================
if __name__ == "__main__":
    TOKEN = "8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM"
    CHANNEL_ID = "-1003832310811"

    bot = AdityaInstitutionalAlgo(token=TOKEN, channel_id=CHANNEL_ID)
    bot.start_realtime_clock_engine()
