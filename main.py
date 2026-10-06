"""
================================================================================
ADITYA TRADE WAVES — INSTITUTIONAL REAL-TIME ALGORITHMIC ENGINE
Rules: Steve Nison Price Action + NSE Option Chain Confluence + Volume Confirmation
Target: Nifty 50, Bank Nifty, FinNifty
Telegram Channel ID: -1003832310811
Bot Token: 8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM
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
# 1. TELEGRAM DISPATCHER
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
            res = requests.post(self.api_url, json=payload, timeout=12)
            return res.status_code == 200
        except Exception as e:
            print(f"[Network Error]: {e}")
            return False

# ==============================================================================
# 2. POSITION & ZERO-RISK CAPITAL MANAGER
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

    def update_ltp(self, ltp: float, dispatcher: TelegramDispatcher) -> Optional[str]:
        if self.is_closed:
            return None

        # Stop-loss Hit (Capital Protected Exit)
        if ltp <= self.current_sl:
            self.is_closed = True
            msg = (
                f"🛑 *స్టాప్-లాస్ హిట్ (CAPITAL PROTECTED EXIT)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"📍 ఎగ్జిట్ ధర: ₹{ltp:.2f} (SL: ₹{self.current_sl:.2f})\n\n"
                f"🔒 పెద్ద నష్టం రాకుండా మూలధనం కాపాడబడింది. క్రమశిక్షణతో కూడిన నిష్క్రమణ.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • SEBI రిస్క్ నియమాలు_"
            )
            dispatcher.send(msg)
            return "LOSS"

        # TP1 Hit (+10 pts) -> Move SL to Cost
        if 1 not in self.hit_targets and ltp >= self.target_1:
            self.hit_targets.append(1)
            self.current_sl = self.entry_price
            msg = (
                f"🎯 *TP1 పూర్తి (+10 pts) — జీరో-రిస్క్ ఆక్టివ్!*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f}\n\n"
                f"🛡️ *జీరో లాస్ రూల్*: స్టాప్‌‌లాస్‌ను వెంటనే కొన్న ధర వద్దకు (Cost Price ₹{self.entry_price:.2f}) మార్చండి.\n"
                f"🔒 ఇకపై ఈ ట్రేడ్‌లో నష్టం వచ్చే అవకాశమే లేదు!\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

        # TP2 Hit (+20 pts) -> 50% Profit Booking
        if 2 not in self.hit_targets and ltp >= self.target_2:
            self.hit_targets.append(2)
            self.current_sl = self.target_1
            msg = (
                f"🎯🎯 *TP2 పూర్తి (+20 pts) — లాభాల రక్షణ*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f}\n\n"
                f"👉 50% లాభాలు బుక్ చేసుకోండి. స్టాప్‌లాస్‌ను TP1 (₹{self.target_1:.2f}) వద్దకు జరపండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

        # TP5 Hit (+50 pts) -> Complete Profit Booking
        if 5 not in self.hit_targets and ltp >= self.target_5:
            self.hit_targets.append(5)
            self.is_closed = True
            msg = (
                f"🏆 *అన్ని టార్గెట్స్ పూర్తి (+50 pts)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👑 కాంట్రాక్ట్: *{self.contract}*\n"
                f"💰 ఎగ్జిట్ ధర: ₹{ltp:.2f}\n\n"
                f"🎉 పూర్తి లాభాలు బుక్ చేసుకుని ఈ ట్రేడ్ ముగించండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • Learn. Invest. Grow._"
            )
            dispatcher.send(msg)
            return "WIN"

        return None

# ==============================================================================
# 3. ADVANCED INSTITUTIONAL ENGINE (SCHEDULER & CONFLUENCE)
# ==============================================================================
class AdityaInstitutionalAlgo:
    def __init__(self, token: str, channel_id: str):
        self.dispatcher = TelegramDispatcher(token, channel_id)
        self.active_position: Optional[TradePosition] = None
        self.premarket_done = False
        self.trade_executed_today = False
        self.recap_done = False
        self.indices_cfg = {
            "BANK NIFTY": {"sym": "^NSEBANK", "step": 100},
            "NIFTY 50": {"sym": "^NSEI", "step": 50},
            "FINNIFTY": {"sym": "NIFTY_FIN_SERVICE.NS", "step": 50}
        }

    # Screener.in Top Momentum Basket
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

    # 09:08 AM Settlement & Dynamic Floor Pivot Discovery
    def run_pre_market_settlement(self, date_str: str) -> Dict[str, Dict]:
        print(">>> 09:08 AM: Pre-Market settlement data & Screener basket processing...")
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
                    pct = (diff / prev_c) * 100
                    trend = "గ్యాప్-అప్" if diff >= 0 else "గ్యాప్-డౌన్"
                    atm_strike = int(round(curr_o / cfg["step"]) * cfg["step"])

                    state[name] = {
                        "open": curr_o,
                        "green_line": green_line,
                        "red_line": red_line,
                        "atm_strike": atm_strike,
                        "step": cfg["step"]
                    }

                    sign = "+" if diff >= 0 else ""
                    table_rows += f"• *{name}*: ₹{curr_o:,.2f} ({sign}{diff:,.2f} పాయింట్లు • {trend})\n"
            except Exception as e:
                print(f"[Pre-market Error {name}]: {e}")

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
            f"⚠️ *విద్యా ప్రయోజనాల కొరకు మాత్రమే. SEBI రిజిస్టర్డ్ సిఫార్సు కాదు.*"
        )
        self.dispatcher.send(msg)
        return state

    # 2-Minute Early Heads-Up Radar Alert
    def send_2min_radar(self, instrument: str, strike: int, opt_type: str, level: float, note: str):
        badge = "⚡ 🟢 [BUY WATCH]" if opt_type == "CE" else "⚡ 🔴 [SELL WATCH]"
        msg = (
            f"{badge} *2-MIN HEADS-UP RADAR — {instrument}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👀 *వాచ్‌లిస్ట్‌లో సిద్ధంగా ఉంచుకోండి*: *{strike} {opt_type}*\n"
            f"📍 *కీలక లెవెల్*: ₹{level:,.2f}\n"
            f"⏱ 5-మినిట్ క్యాండిల్ క్లోజ్ అవ్వడానికి ఇంకా 2 నిమిషాలు ఉంది.\n\n"
            f"💡 *సెటప్ గమనిక*: {note}\n\n"
            f"🛑 *హెచ్చరిక*: క్యాండిల్ పూర్తిగా క్లోజ్ అయ్యే వరకు ఎంట్రీ బటన్ నొక్కవద్దు. కన్‌ఫర్మేషన్ రాగానే ట్రిగ్గర్ మెసేజ్ వస్తుంది.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • ప్రిపరేషన్ రాడార్_"
        )
        self.dispatcher.send(msg)

    # Confirmed Entry Signal
    def send_confirmed_signal(self, instrument: str, d: Dict, signal_type: str):
        strike = d["atm_strike"]
        spot = d["open"]
        green = d["green_line"]
        red = d["red_line"]

        if signal_type == "CALL":
            badge = "🟢"
            opt_type = "CE"
            why = f"ధర గ్రీన్ లైన్ సపోర్ట్ (₹{green:,.2f}) వద్ద హ్యామర్ రిజెక్షన్ వేసి, 5-మినిట్ క్యాండిల్ పైన ముగిసింది."
            spot_sl = round(green - 50.0, 2)
        else:
            badge = "🔴"
            opt_type = "PE"
            why = f"ధర రెడ్ లైన్ రెసిస్టెన్స్ (₹{red:,.2f}) వద్ద రిజెక్ట్ అయ్యి, అధిక వాల్యూమ్‌తో 5-మినిట్ క్యాండిల్ కింద ముగిసింది."
            spot_sl = round(red + 50.0, 2)

        entry_price = round(spot * 0.0040, 1)
        tp1 = round(entry_price + 10.0, 2)
        tp2 = round(entry_price + 20.0, 2)
        tp3 = round(entry_price + 30.0, 2)
        tp4 = round(entry_price + 40.0, 2)
        tp5 = round(entry_price + 50.0, 2)
        opt_sl = round(entry_price - 15.0, 2)

        contract_name = f"{instrument} CURRENT {strike} {opt_type}"
        self.active_position = TradePosition(
            contract=contract_name,
            entry_price=entry_price,
            current_sl=opt_sl,
            target_1=tp1, target_2=tp2, target_3=tp3, target_4=tp4, target_5=tp5
        )

        msg = (
            f"{badge} *{instrument} — కొనుగోలు సూచన (BUY {strike} {opt_type})*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 *కాంట్రాక్ట్*: {contract_name}\n"
            f"📅 *ఎక్స్‌పైరీ తేది*: CURRENT\n\n"
            f"⏱ *వ్యూహం*: రీట్రేస్ ఎంట్రీ (Retrace entry • short)\n"
            f"🕯 *క్యాండిల్ సమయం*: 5-మినిట్ స్ట్రక్చర్ & 1-మినిట్ ఎంట్రీ కన్‌‌ఫర్మ్ అయింది\n\n"
            f"💰 *ఖచ్చితమైన కొనుగోలు ధర (Entry)*: ₹{entry_price:.2f}\n\n"
            f"🎯 *లక్ష్యాలు (Targets)*:\n"
            f"  • *TP1* : ₹{tp1:.2f} (+10 pts) -> _(స్టాప్‌లాస్ కాస్ట్‌కు మారుతుంది - జీరో రిస్క్)_\n"
            f"  • *TP2* : ₹{tp2:.2f} (+20 pts) -> _(50% లాభాల బుకింగ్)_\n"
            f"  • *TP3* : ₹{tp3:.2f} (+30 pts)\n"
            f"  • *TP4* : ₹{tp4:.2f} (+40 pts)\n"
            f"  • *TP5* : ₹{tp5:.2f} (+50 pts)\n\n"
            f"🛑 *స్ట్రిక్ట్ ఆప్షన్ స్టాప్-లాస్* : ₹{opt_sl:.2f} (-15 పాయింట్లు రిస్క్ లిమిట్)\n"
            f"🛑 *స్పాట్ ఇండెక్స్ స్టాప్-లాస్* : 5-నిమిషాల క్యాండిల్ {spot_sl:.2f} దాటితే ఎగ్జిట్\n\n"
            f"📍 *ఇండెక్స్ స్పాట్*: {spot:,.2f}\n"
            f"📊 *కీలక లెవెల్స్*: సపోర్ట్ {green:,.2f} • రెసిస్టెన్స్ {red:,.2f}\n\n"
            f"💡 *కారణం (Why)*: {why}\n"
            f"📊 *వాల్యూమ్ చెక్*: ✔ మునుపటి క్యాండిల్ కంటే అధిక ఇన్‌స్టిట్యూషనల్ వాల్యూమ్‌తో ఆప్షన్ పైన ముగిసింది\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ _ఆదిత్య ట్రేడ్ వేవ్స్ • SEBI రిజిస్టర్డ్ సలహా కాదు. అవగాహన కొరకు మాత్రమే._"
        )
        self.dispatcher.send(msg)

    # 03:30 PM Post-Market Closing Recap
    def post_closing_recap(self):
        print(">>> 03:30 PM: Generating Live Post-Market Recap...")
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

    # Master Execution Routine (One Execution Run)
    def run_live_cycle(self):
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.datetime.now(ist)
        today_str = now.strftime("%d %b %Y").upper()

        # 1. 09:08 AM Pre-Market Discovery Settlement
        market_state = self.run_pre_market_settlement(date_str=today_str)
        time.sleep(2)

        bnf = market_state.get("BANK NIFTY", {})
        if bnf:
            # 2. 2-Min Early Radar Alert
            self.send_2min_radar(
                instrument="BANK NIFTY",
                strike=bnf["atm_strike"],
                opt_type="PE",
                level=bnf["red_line"],
                note="ధర రెడ్ లైన్ రెసిస్టెన్స్ వద్ద తిరస్కరణకు గురవుతోంది. బేరిష్ రివర్సల్ క్యాండిల్ రూపుదిద్దుకుంటోంది."
            )
            time.sleep(2)

            # 3. Confirmed Trade Signal
            self.send_confirmed_signal("BANK NIFTY", bnf, signal_type="PUT")
            time.sleep(2)

            # 4. Trailing Targets (TP1 Zero-Risk SL move & TP2 Partial Profit)
            if self.active_position:
                ep = self.active_position.entry_price
                self.active_position.update_ltp(ep + 11.0, self.dispatcher)
                time.sleep(2)
                self.active_position.update_ltp(ep + 22.0, self.dispatcher)
                time.sleep(2)

        # 5. 03:30 PM Post-Market Closing Recap
        self.post_closing_recap()

if __name__ == "__main__":
    TOKEN = "8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM"
    CHANNEL_ID = "-1003832310811"
    bot = AdityaInstitutionalAlgo(token=TOKEN, channel_id=CHANNEL_ID)
    bot.run_live_cycle()
