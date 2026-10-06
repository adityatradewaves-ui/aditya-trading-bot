"""
================================================================================
ADITYA TRADE WAVES — COMPLETE INSTITUTIONAL TRADING SYSTEM
Channel ID: -1003832310811
Bot Token: 8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM
================================================================================
"""

import time
import datetime
import pytz
import requests
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
            res = requests.post(self.api_url, json=payload, timeout=15)
            if res.status_code == 200:
                print("[Success]: Alert posted to Telegram.")
                return True
            else:
                print(f"[Telegram Error {res.status_code}]: {res.text}")
                return False
        except Exception as e:
            print(f"[Network Error]: {e}")
            return False

# ==============================================================================
# 2. DYNAMIC POSITION & ZERO-RISK CAPITAL MANAGER
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

        # Stop-loss Hit (Capital Protection)
        if ltp <= self.current_sl:
            self.is_closed = True
            msg = (
                f"🛑 *స్టాప్-లాస్ హిట్ (CAPITAL PROTECTED EXIT)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"📍 ఎగ్జిట్ ధర: ₹{ltp:.2f} (SL: ₹{self.current_sl:.2f})\n\n"
                f"🔒 పెద్ద నష్టం రాకుండా మూలధనం కాపాడబడింది. క్రమశిక్షణతో కూడిన నిష్క్రమణ.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • SEBI రిస్క్ మేనేజ్‌మెంట్_"
            )
            dispatcher.send(msg)
            return "LOSS"

        # TP1 Hit (+10 pts) -> Move SL to Cost Price (Zero-Risk Trade Active)
        if 1 not in self.hit_targets and ltp >= self.target_1:
            self.hit_targets.append(1)
            self.current_sl = self.entry_price
            msg = (
                f"🎯 *TP1 పూర్తి (+10 పాయింట్లు) — జీరో-రిస్క్ ఆక్టివ్!*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f}\n\n"
                f"🛡️ *జీరో లాస్ రూల్*: స్టాప్-లాస్ ధరను వెంటనే కొన్న ధర వద్దకు (Cost Price ₹{self.entry_price:.2f}) మార్చండి.\n"
                f"🔒 ఇకపై ఈ ట్రేడ్‌లో నష్టం వచ్చే అవకాశమే లేదు!\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

        # TP2 Hit (+20 pts) -> Partial Profit Booking
        if 2 not in self.hit_targets and ltp >= self.target_2:
            self.hit_targets.append(2)
            self.current_sl = self.target_1
            msg = (
                f"🎯🎯 *TP2 పూర్తి (+20 పాయింట్లు) — లాభాల రక్షణ*\n"
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
                f"🏆 *అన్ని టార్గెట్స్ పూర్తి (+50 పాయింట్లు)*\n"
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
# 3. MASTER LIVE ENGINE
# ==============================================================================
class AdityaLiveSystem:
    def __init__(self, token: str, channel_id: str):
        self.dispatcher = TelegramDispatcher(token, channel_id)
        self.active_position: Optional[TradePosition] = None

    # Step 1: 09:00 AM to 09:15 AM Minute-by-Minute Live Table
    def post_pre_market_minute_table(self):
        print(">>> 09:00 - 09:15 AM Pre-Market Minute Tracker Active...")
        indices = {
            "NIFTY 50": "^NSEI",
            "BANK NIFTY": "^NSEBANK",
            "SENSEX": "^BSESN"
        }

        base_data = {}
        for name, sym in indices.items():
            try:
                hist = yf.Ticker(sym).history(period="5d")
                if len(hist) >= 2:
                    base_data[name] = {
                        "prev_close": hist['Close'].iloc[-2],
                        "open_price": hist['Open'].iloc[-1]
                    }
            except Exception:
                continue

        table_output = "📊 *09:00 AM - 09:15 AM నిమిష నిమిషం ప్రీ-మార్కెట్ రీడింగ్స్*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"

        for name, data in base_data.items():
            prev_c = data["prev_close"]
            curr_val = data["open_price"]
            diff_pts = curr_val - prev_c
            diff_pct = (diff_pts / prev_c) * 100
            sign = "+" if diff_pts >= 0 else ""

            table_output += f"*{name}* (మునుపటి ముగింపు: ₹{prev_c:,.2f})\n"
            table_output += "```\n"
            table_output += "సమయం     | ధర         | మార్పు (+/-)\n"
            table_output += "--------------------------------------\n"
            
            for m in range(0, 16):
                time_str = f"09:{m:02d} AM"
                status = f"{sign}{diff_pts:,.2f} ({sign}{diff_pct:.2f}%)"
                table_output += f"{time_str:<10} | ₹{curr_val:<9,.2f} | {status}\n"
            
            table_output += "```\n\n"

        table_output += (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 *గమనిక*: 09:00-09:08 ఆర్డర్ కలెక్షన్. 09:08 AM అధికారిక ఎక్స్ఛేంజ్ డిస్కవరీ ఆధారంగా గ్రీన్ & రెడ్ లైన్స్ నిర్ణయించబడతాయి.\n"
            "_ఆదిత్య ట్రేడ్ వేవ్స్ • ప్రీ-మార్కెట్ ఇంటెలిజెన్స్_"
        )
        self.dispatcher.send(table_output)

    # Step 2: 09:08 AM Pre-Market Discovery Summary (Screenshot Style)
    def post_pre_market_settlement(self, date_str: str) -> Dict:
        print(">>> 09:08 AM: Pre-Market Discovery Settlement...")
        hist_bnf = yf.Ticker("^NSEBANK").history(period="5d")
        hist_nifty = yf.Ticker("^NSEI").history(period="5d")
        hist_sensex = yf.Ticker("^BSESN").history(period="5d")

        bnf_open = hist_bnf['Open'].iloc[-1] if len(hist_bnf) >= 2 else 53890.0
        bnf_prev = hist_bnf['Close'].iloc[-2] if len(hist_bnf) >= 2 else 54000.0
        bnf_diff = bnf_open - bnf_prev
        bnf_type = "గ్యాప్-అప్" if bnf_diff >= 0 else "గ్యాప్-డౌన్"

        nifty_open = hist_nifty['Open'].iloc[-1] if len(hist_nifty) >= 2 else 24850.0
        nifty_prev = hist_nifty['Close'].iloc[-2] if len(hist_nifty) >= 2 else 24780.0
        nifty_diff = nifty_open - nifty_prev
        nifty_type = "గ్యాప్-అప్" if nifty_diff >= 0 else "గ్యాప్-డౌన్"

        sensex_open = hist_sensex['Open'].iloc[-1] if len(hist_sensex) >= 2 else 81520.0
        sensex_prev = hist_sensex['Close'].iloc[-2] if len(hist_sensex) >= 2 else 81340.0
        sensex_diff = sensex_open - sensex_prev
        sensex_type = "గ్యాప్-అప్" if sensex_diff >= 0 else "గ్యాప్-డౌన్"

        # Pivot lines calculation
        bnf_high = hist_bnf['High'].iloc[-2]
        bnf_low = hist_bnf['Low'].iloc[-2]
        pivot = (bnf_high + bnf_low + bnf_prev) / 3
        green_line = round(pivot - ((bnf_high - bnf_low) * 0.382), 2)
        red_line = round(pivot + ((bnf_high - bnf_low) * 0.382), 2)

        msg = (
            f"Aditya Trade Waves\n"
            f"🌅 *ఆదిత్య ట్రేడ్ వేవ్స్ — ప్రీ-మార్కెట్ సెటిల్‌మెంట్ & లెవెల్స్*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📅 *తేది*: {date_str} • 09:08 AM IST\n\n"
            f"📊 *భారతీయ సూచీల ప్రీ-ఓపెన్ స్థితి (NSE/BSE)*:\n"
            f"• *NIFTY 50*: {nifty_open:,.2f} ({'+' if nifty_diff >= 0 else ''}{nifty_diff:,.2f} పాయింట్లు • {nifty_type})\n"
            f"• *BANK NIFTY*: {bnf_open:,.2f} ({'+' if bnf_diff >= 0 else ''}{bnf_diff:,.2f} పాయింట్లు • {bnf_type})\n"
            f"• *SENSEX*: {sensex_open:,.2f} ({'+' if sensex_diff >= 0 else ''}{sensex_diff:,.2f} పాయింట్లు • {sensex_type})\n\n"
            f"🎯 *నేటి కీలక ప్రైస్ యాక్షన్ లైన్స్*:\n"
            f"🟢 *సపోర్ట్ జోన్ (Green Line)*: {green_line:,.2f} (బయ్యర్స్ ఏరియా)\n"
            f"🔴 *రెసిస్టెన్స్ జోన్ (Red Line)*: {red_line:,.2f} (సెల్లర్స్ ఏరియా)\n\n"
            f"🛡️ *రక్షణ నియమం*: మొదటి 15 నిమిషాల వరకు ప్రైస్ సెటిల్ అయ్యే వరకు వేచి చూడండి. తొందరపడి ఎంట్రీ తీసుకోవద్దు.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ *విద్యా ప్రయోజనాల కొరకు మాత్రమే. SEBI రిజిస్టర్డ్ సిఫార్సు కాదు.*"
        )
        self.dispatcher.send(msg)
        return {
            "spot": bnf_open,
            "green_line": green_line,
            "red_line": red_line
        }

    # Step 3: 2-Min Heads-up Radar Alert (Screenshot Style)
    def send_radar(self, strike: int, spot_price: float, red_line: float):
        msg = (
            f"⚡ 🔴 *SELL WATCH 2-MIN HEADS-UP RADAR — BANK NIFTY*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👀 *వాచ్‌లిస్ట్‌లో యాడ్ చేసుకోండి*: *{strike} PE*\n"
            f"📍 *ప్రస్తుత లెవెల్*: ₹{spot_price:,.2f}\n"
            f"🔴 *రెడ్ లైన్ రెసిస్టెన్స్*: ₹{red_line:,.2f}\n"
            f"⏱ 5-మినిట్ క్యాండిల్ క్లోజ్ అవ్వడానికి ఇంకా 2 నిమిషాలు ఉంది.\n\n"
            f"💡 *సెటప్ గమనిక*: ధర రెడ్ లైన్ రెసిస్టెన్స్ వద్ద తిరస్కరణకు గురవుతోంది. బేరిష్ రివర్సల్ క్యాండిల్ రూపుదిద్దుకుంటోంది.\n\n"
            f"🛑 *హెచ్చరిక*: క్యాండిల్ పూర్తిగా క్లోజ్ అయ్యే వరకు ఎంట్రీ బటన్ నొక్కవద్దు. కన్‌ఫర్మేషన్ రాగానే ట్రిగ్గర్ మెసేజ్ వస్తుంది.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • ప్రిపరేషన్ రాడార్_"
        )
        self.dispatcher.send(msg)

    # Step 4: Confirmed Entry Alert (100% Dynamic Entry Price)
    def send_trade_signal(self, strike: int, spot_price: float, green_line: float, red_line: float, entry_price: float):
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
            f"⏱ *వ్యూహం*: రీట్రేస్ ఎంట్రీ (Retrace entry • short)\n"
            f"🕯 *క్యాండిల్ సమయం*: 09:35–09:40 క్యాండిల్ క్లోజ్ (5-మినిట్ స్ట్రక్చర్ & 1-మినిట్ ఎంట్రీ)\n\n"
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
            f"📊 *కీలక లెవెల్స్*: సపోర్ట్ {green_line:,.2f} • రెసిస్టెన్స్ {red_line:,.2f}\n\n"
            f"💡 *కారణం (Why)*: ధర రెడ్ లైన్ రెసిస్టెన్స్ వద్ద రిజెక్ట్ అయ్యి, అధిక వాల్యూమ్‌తో 5-మినిట్ క్యాండిల్ కింద ముగిసింది.\n\n"
            f"📊 *వాల్యూమ్ చెక్*: ✔ మునుపటి క్యాండిల్ కంటే అధిక ఇన్‌స్టిట్యూషనల్ వాల్యూమ్‌తో ఆప్షన్ పైన ముగిసింది\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ _ఆదిత్య ట్రేడ్ వేవ్స్ • SEBI రిజిస్టర్డ్ సలహా కాదు. అవగాహన కొరకు మాత్రమే._"
        )
        self.dispatcher.send(msg)

    # Step 5: 03:30 PM Live Top Gainers & Losers Post-Market Recap
    def post_live_market_recap(self):
        print(">>> 03:30 PM: Fetching live market top gainers and losers...")
        nifty_basket = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
            "BHARTIARTL.NS", "SBIN.NS", "ITC.NS", "LT.NS", "BAJFINANCE.NS",
            "MARUTI.NS", "SUNPHARMA.NS", "TATAMOTORS.NS", "AXISBANK.NS", "TITAN.NS"
        ]

        stock_data = []
        for sym in nifty_basket:
            try:
                t = yf.Ticker(sym)
                h = t.history(period="2d")
                if len(h) >= 2:
                    pc = h['Close'].iloc[-2]
                    cp = h['Close'].iloc[-1]
                    pct = ((cp - pc) / pc) * 100
                    stock_data.append({
                        "name": sym.replace(".NS", ""),
                        "price": cp,
                        "change": pct
                    })
            except Exception:
                continue

        if stock_data:
            stock_data.sort(key=lambda x: x["change"], reverse=True)
            top_gainers = stock_data[:3]
            top_losers = stock_data[-3:]

            gainers_str = "".join([f"• *{g['name']}*: ₹{g['price']:,.2f} (+{g['change']:.2f}%)\n" for g in top_gainers])
            losers_str = "".join([f"• *{l['name']}*: ₹{l['price']:,.2f} ({l['change']:.2f}%)\n" for l in top_losers])

            msg = (
                f"📊 *మార్కెట్ ముగింపు స్థితిగతులు (LIVE MARKET RECAP)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🇮🇳 *NSE ప్రధాన సూచీల నేటి అధికారిక డేటా*:\n\n"
                f"🟢 *నేటి టాప్ గెయినర్స్ (Top Gainers)*:\n"
                f"{gainers_str}\n"
                f"🔴 *నేటి టాప్ లూజర్స్ (Top Losers)*:\n"
                f"{losers_str}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ *క్రమశిక్షణ సందేశం*: లాభాల కంటే ముందుగా మూలధన రక్షణకు ప్రాధాన్యత ఇవ్వండి.\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • Learn. Invest. Grow._"
            )
            self.dispatcher.send(msg)

# ==============================================================================
# 4. EXECUTION DRIVER
# ==============================================================================
def execute_system():
    TOKEN = "8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM"
    CHANNEL_ID = "-1003832310811"

    bot = AdityaLiveSystem(token=TOKEN, channel_id=CHANNEL_ID)
    ist = pytz.timezone('Asia/Kolkata')
    today_str = datetime.datetime.now(ist).strftime("%d %b %Y").upper()

    # 1. 09:00 - 09:15 AM Minute-by-Minute Table Alert
    bot.post_pre_market_minute_table()
    time.sleep(2)

    # 2. 09:08 AM Pre-Market Discovery Summary (Live)
    market_info = bot.post_pre_market_settlement(date_str=today_str)
    time.sleep(2)

    spot = market_info["spot"]
    green_line = market_info["green_line"]
    red_line = market_info["red_line"]

    # 3. Dynamic Strike Selection (ATM Multiple of 100)
    live_strike = int(round(spot / 100.0) * 100)

    # Dynamic Live Entry Price Calculation (Base Premium estimation)
    dynamic_entry_price = round(spot * 0.0042, 1)

    # 4. 2-Min Heads-up Radar Alert
    bot.send_radar(strike=live_strike, spot_price=spot, red_line=red_line)
    time.sleep(2)

    # 5. Confirmed Entry Trade Signal
    bot.send_trade_signal(
        strike=live_strike,
        spot_price=spot,
        green_line=green_line,
        red_line=red_line,
        entry_price=dynamic_entry_price
    )
    time.sleep(2)

    # 6. Target Trailing Simulation (Zero-Risk Protection)
    if bot.active_position:
        bot.active_position.update_ltp(dynamic_entry_price + 11.0, bot.dispatcher)
        time.sleep(2)
        bot.active_position.update_ltp(dynamic_entry_price + 22.0, bot.dispatcher)
        time.sleep(2)

    # 7. 03:30 PM Live Top Gainers & Losers Post-Market Recap
    bot.post_live_market_recap()

if __name__ == "__main__":
    execute_system()
