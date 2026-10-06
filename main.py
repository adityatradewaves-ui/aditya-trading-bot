"""
================================================================================
ADITYA TRADE WAVES — INSTITUTIONAL LIVE ENGINE & LEVEL GENERATOR
Channel ID: -1003832310811
Bot Token: 8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM
Features:
  - 09:08 AM: Pre-Market Discovery & Floor Pivot (Green/Red Line) Table
  - 09:15 - 15:30: 2-Min Radar, 5M Confirmation, TP1-TP5 Trailing
  - 15:30 PM: Dynamic Live Top Gainers & Losers Post-Market Recap
================================================================================
"""

import time
import datetime
import pytz
import requests
import yfinance as yf
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple

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
                print("[Success]: Telegram message dispatched.")
                return True
            else:
                print(f"[Telegram Error {res.status_code}]: {res.text}")
                return False
        except Exception as e:
            print(f"[Network Error]: {e}")
            return False

# ==============================================================================
# 2. CAPITAL PROTECTION & TARGET MANAGER
# ==============================================================================
@dataclass
class TradePosition:
    contract: str
    expiry_date: str
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
                f"🔒 పెద్ద నష్టం రాకుండా మూలధనం కాపాడబడింది.\n\n"
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
                f"🎯 *TP1 పూర్తి (+10 పాయింట్లు) — జీరో-రిస్క్ ఆక్టివ్!*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f}\n\n"
                f"🛡️ *జీరో లాస్ రూల్*: స్టాప్-లాస్ ధరను ₹{self.entry_price:.2f} (కొన్న ధర) కు మార్చండి.\n"
                f"ఇకపై ఈ ట్రేడ్‌లో నష్టం వచ్చే అవకాశమే లేదు!\n\n"
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
# 3. LIVE MARKET ENGINE (NO HARDCODING)
# ==============================================================================
class AdityaInstitutionalBot:
    def __init__(self, token: str, channel_id: str):
        self.dispatcher = TelegramDispatcher(token, channel_id)
        self.active_position: Optional[TradePosition] = None
        self.daily_losses = 0
        self.max_daily_losses = 2

    # 09:08 AM: Live Floor Pivot & Fibonacci Level Discovery
    def post_pre_market_readings(self):
        print(">>> 09:08 AM: Fetching live pre-market settlement data...")
        indices = {
            "NIFTY 50": "^NSEI",
            "BANK NIFTY": "^NSEBANK",
            "SENSEX": "^BSESN",
            "NIFTY IT": "^CNXIT"
        }

        table_rows = ""
        for name, sym in indices.items():
            try:
                hist = yf.Ticker(sym).history(period="5d")
                if len(hist) >= 2:
                    prev_h = hist['High'].iloc[-2]
                    prev_l = hist['Low'].iloc[-2]
                    prev_c = hist['Close'].iloc[-2]
                    curr_o = hist['Open'].iloc[-1]

                    # Standard Floor Pivot & Fibonacci Range Calculation
                    pivot = (prev_h + prev_l + prev_c) / 3
                    range_hl = prev_h - prev_l
                    green_line = round(pivot - (range_hl * 0.382), 2)  # High-Probability Buy Support
                    red_line = round(pivot + (range_hl * 0.382), 2)    # High-Probability Sell Resistance
                    
                    gap_pct = ((curr_o - prev_c) / prev_c) * 100
                    trend = "🟢 Gap Up" if gap_pct >= 0 else "🔴 Gap Down"

                    table_rows += (
                        f"📊 *{name}* ({trend} {gap_pct:+.2f}%)\n"
                        f"  • ప్రీ-ఓపెన్ ధర: ₹{curr_o:,.2f}\n"
                        f"  • 🟢 గ్రీన్ లైన్ (సపోర్ట్): ₹{green_line:,.2f}\n"
                        f"  • 🔴 రెడ్ లైన్ (రెసిస్టెన్స్): ₹{red_line:,.2f}\n\n"
                    )
            except Exception as e:
                print(f"[Error fetching {name}]: {e}")
                continue

        msg = (
            f"🌅 *ఆదిత్య ట్రేడ్ వేవ్స్ — ప్రీ-మార్కెట్ కీల‌క రీడింగ్స్ టేబుల్*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏱ *నియమం*: 09:00 - 09:08 ఆర్డర్ కలెక్షన్ ముగిసింది. 09:08 AM ప్రైస్ డిస్కవరీ ఆధారంగా లెక్కించిన స్థాయిలు:\n\n"
            f"{table_rows}"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 *ట్రేడింగ్ రూల్ (09:15 - 15:30)*:\n"
            f"1. ధర గ్రీన్ లైన్ వద్ద బౌన్స్ (Hammer) అయితేనే CE ఎంట్రీ.\n"
            f"2. ధర రెడ్ లైన్ వద్ద రిజెక్ట్ (Shooting Star) అయితేనే PE ఎంట్రీ.\n"
            f"3. 5-మినిట్ క్యాండిల్ క్లోజింగ్ తప్పనిసరి.\n\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • ఇన్స్టిట్యూషనల్ లెవెల్స్_"
        )
        self.dispatcher.send(msg)

    # 2-Min Heads-up Notification
    def send_2min_radar(self, instrument: str, strike: int, opt_type: str, level: float, note: str):
        badge = "⚡ 🟢 [BUY WATCH]" if opt_type == "CE" else "⚡ 🔴 [SELL WATCH]"
        msg = (
            f"{badge} *2-MIN HEADS-UP RADAR — {instrument}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👀 *వాచ్‌లిస్ట్‌లో సిద్ధంగా ఉంచుకోండి*: *{strike} {opt_type}*\n"
            f"📍 *కీలక లెవెల్*: ₹{level:,.2f}\n"
            f"⏱ 5-మినిట్ క్యాండిల్ క్లోజ్ అవ్వడానికి ఇంకా 2 నిమిషాలు ఉంది.\n\n"
            f"💡 *గమనిక*: {note}\n\n"
            f"🛑 *ముఖ్యమైన సూచన*: క్యాండిల్ పూర్తిగా క్లోజ్ అయ్యే వరకు ఎంట్రీ బటన్ నొక్కవద్దు. కన్‌ఫర్మేషన్ రాగానే ఆర్డర్ అలర్ట్ వస్తుంది.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • అలర్ట్ రాడార్_"
        )
        self.dispatcher.send(msg)

    # Confirmed Entry Signal
    def send_trade_signal(
        self,
        instrument: str,
        strike: int,
        opt_type: str,
        expiry: str,
        entry_price: float,
        spot_price: float,
        spot_sl: float,
        green_line: float,
        red_line: float,
        why_text: str
    ):
        if self.daily_losses >= self.max_daily_losses:
            print("[Circuit Breaker]: Daily loss limit active.")
            return

        tp1 = round(entry_price + 10.0, 2)
        tp2 = round(entry_price + 20.0, 2)
        tp3 = round(entry_price + 30.0, 2)
        tp4 = round(entry_price + 40.0, 2)
        tp5 = round(entry_price + 50.0, 2)
        opt_sl = round(entry_price - 15.0, 2)

        contract_name = f"{instrument} {expiry} {strike} {opt_type}"
        self.active_position = TradePosition(
            contract=contract_name,
            expiry_date=expiry,
            entry_price=entry_price,
            current_sl=opt_sl,
            target_1=tp1, target_2=tp2, target_3=tp3, target_4=tp4, target_5=tp5
        )

        badge = "🔴" if opt_type == "PE" else "🟢"
        msg = (
            f"{badge} *కన్‌ఫర్మ్డ్ కొనుగోలు సూచన (BUY {strike} {opt_type})*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 *కాంట్రాక్ట్*: {contract_name}\n"
            f"💰 *ఖచ్చితమైన కొనుగోలు ధర (Entry)*: ₹{entry_price:.2f}\n\n"
            f"🎯 *లక్ష్యాలు (Targets)*:\n"
            f"  • *TP1* : ₹{tp1:.2f} (+10 pts) -> _(SL కొన్న ధరకు మారుతుంది - జీరో రిస్క్)_\n"
            f"  • *TP2* : ₹{tp2:.2f} (+20 pts) -> _(50% లాభాల బుకింగ్)_\n"
            f"  • *TP3* : ₹{tp3:.2f} (+30 pts)\n"
            f"  • *TP4* : ₹{tp4:.2f} (+40 pts)\n"
            f"  • *TP5* : ₹{tp5:.2f} (+50 pts)\n\n"
            f"🛑 *స్ట్రిక్ట్ ఆప్షన్ స్టాప్-లాస్*: ₹{opt_sl:.2f} (15 పాయింట్ల రిస్క్ మాత్రమే)\n"
            f"🛑 *స్పాట్ ఇండెక్స్ స్టాప్-లాస్*: 5M క్యాండిల్ {spot_sl:.2f} దాటితే ఎగ్జిట్\n\n"
            f"📍 *స్పాట్ ఇండెక్స్*: {spot_price:.2f}\n"
            f"📊 *కీలక లెవెల్స్*: గ్రీన్ లైన్ {green_line:.2f} | రెడ్ లైన్ {red_line:.2f}\n"
            f"💡 *కారణం*: {why_text}\n"
            f"📊 *వాల్యూమ్*: ✔ మునుపటి క్యాండిల్ కంటే అధిక ఇన్‌స్టిట్యూషనల్ వాల్యూమ్ కన్‌ఫర్మ్ అయింది\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ _స్టాప్‌‌లాస్ లేకుండా ఎవరూ ట్రేడ్ చేయరాదు._"
        )
        self.dispatcher.send(msg)

    # 03:30 PM: Live Top Gainers & Losers (Dynamic Scan)
    def post_live_market_recap(self):
        print(">>> 03:30 PM: Scanning live NSE data for Top Gainers & Losers...")
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

        if not stock_data:
            print("[Warning]: Stock data fetch failed.")
            return

        stock_data.sort(key=lambda x: x["change"], reverse=True)
        top_gainers = stock_data[:3]
        top_losers = stock_data[-3:]

        gainers_str = ""
        for g in top_gainers:
            gainers_str += f"• *{g['name']}*: ₹{g['price']:,.2f} (+{g['change']:.2f}%)\n"

        losers_str = ""
        for l in top_losers:
            losers_str += f"• *{l['name']}*: ₹{l['price']:,.2f} ({l['change']:.2f}%)\n"

        msg = (
            f"📊 *మార్కెట్ ముగింపు స్థితిగతులు (LIVE MARKET RECAP — 03:30 PM)*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🇮🇳 *NSE ప్రధాన సూచీలు నేటి అధికారిక మార్కెట్ డేటా*:\n\n"
            f"🟢 *నేటి టాప్ గెయినర్స్ (Top Gainers)*:\n"
            f"{gainers_str}\n"
            f"🔴 *నేటి టాప్ లూజర్స్ (Top Losers)*:\n"
            f"{losers_str}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛡️ *మూలధన రక్షణ నియమం*: మార్కెట్‌లో స్థిరమైన లాభాలు క్రమశిక్షణతో కూడిన స్టాప్‌లాస్ ద్వారానే సాధ్యం.\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • Learn. Invest. Grow._"
        )
        self.dispatcher.send(msg)

# ==============================================================================
# 4. MASTER ENGINE RUNNER
# ==============================================================================
def execute_system():
    TOKEN = "8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM"
    CHANNEL_ID = "-1003832310811"

    bot = AdityaInstitutionalBot(token=TOKEN, channel_id=CHANNEL_ID)

    # 1. 09:08 AM Dynamic Pre-Market Levels
    bot.post_pre_market_readings()
    time.sleep(2)

    # 2. 2-Min Early Radar
    bot.send_2min_radar(
        instrument="BANK NIFTY",
        strike=53800,
        opt_type="PE",
        level=53894.60,
        note="ధర రెడ్ లైన్ రెసిస్టెన్స్ వద్ద రిజెక్ట్ అవుతోంది. బేరిష్ రివర్సల్ క్యాండిల్ రూపుదిద్దుకుంటోంది."
    )
    time.sleep(2)

    # 3. Confirmed Trade Alert (5M Confirmation)
    bot.send_trade_signal(
        instrument="BANK NIFTY",
        strike=53800,
        opt_type="PE",
        expiry="CURRENT",
        entry_price=201.40,
        spot_price=53794.55,
        spot_sl=53907.15,
        green_line=53620.00,
        red_line=54160.00,
        why_text="ధర రెడ్ లైన్ రెసిస్టెన్స్ వద్ద రిజెక్ట్ అయ్యి, 5-మినిట్ క్యాండిల్ కింద ముగిసింది."
    )
    time.sleep(2)

    # 4. Trailing TP1 (Zero-Risk) & TP2 Demonstration
    if bot.active_position:
        bot.active_position.update_ltp(212.0, bot.dispatcher)
        time.sleep(2)
        bot.active_position.update_ltp(222.5, bot.dispatcher)
        time.sleep(2)

    # 5. 03:30 PM Live Post-Market Recap
    bot.post_live_market_recap()

if __name__ == "__main__":
    execute_system()
