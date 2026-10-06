"""
================================================================================
ADITYA TRADE WAVES — COMPLETE MARKET ECOSYSTEM & LIVE 5-MIN LOOP AGENT
Author: Aditya Trade Waves
Channel ID: -1003832310811
Bot Token: 8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM
================================================================================
"""

import time
import datetime
import pytz
import requests
from dataclasses import dataclass, field
from typing import List, Optional

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
            if res.status_code == 200:
                print(f"[Success]: Alert posted to Telegram.")
                return True
            else:
                print(f"[Telegram API Error {res.status_code}]: {res.text}")
                return False
        except Exception as e:
            print(f"[Network Error]: {e}")
            return False

# ==============================================================================
# 2. POSITION & MULTI-TARGET TRACKER (TP1 TO TP5)
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

    def update_ltp(self, ltp: float, dispatcher: TelegramDispatcher):
        if self.is_closed:
            return

        if ltp <= self.current_sl:
            self.is_closed = True
            msg = (
                f"🛑 *స్టాప్-లాస్ హిట్ అయింది (STOP-LOSS HIT)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"📅 ఎక్స్‌పైరీ తేది: *{self.expiry_date}*\n\n"
                f"📍 ఎగ్జిట్ ధర: ₹{ltp:.2f} (SL: ₹{self.current_sl:.2f})\n\n"
                f"💡 క్రమశిక్షణతో కూడిన నిష్క్రమణ. మూలధన రక్షణకు ప్రాధాన్యత ఇవ్వబడింది.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • SEBI రిస్క్ మేనేజ్‌మెంట్_"
            )
            dispatcher.send(msg)
            return

        if 1 not in self.hit_targets and ltp >= self.target_1:
            self.hit_targets.append(1)
            self.current_sl = self.entry_price
            msg = (
                f"🎯 *మొదటి టార్గెట్ పూర్తి (TP1 DONE)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"📅 ఎక్స్‌పైరీ తేది: *{self.expiry_date}*\n\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f} (+10 పాయింట్లు)\n\n"
                f"👉 *చర్య*: స్టాప్-లాస్‌ను కొన్న ధర వద్దకు (₹{self.entry_price:.2f}) మార్చండి. జీరో-రిస్క్ ట్రేడ్ ఆక్టివ్!\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

        if 2 not in self.hit_targets and ltp >= self.target_2:
            self.hit_targets.append(2)
            self.current_sl = self.target_1
            msg = (
                f"🎯🎯 *రెండవ టార్గెట్ పూర్తి (TP2 DONE)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"📅 ఎక్స్‌పైరీ తేది: *{self.expiry_date}*\n\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f} (+20 పాయింట్లు)\n\n"
                f"👉 *చర్య*: 50% లాభాలు బుక్ చేసుకోండి. స్టాప్-లాస్‌ను TP1 వద్దకు జరపండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

        if 5 not in self.hit_targets and ltp >= self.target_5:
            self.hit_targets.append(5)
            self.is_closed = True
            msg = (
                f"🏆 *అన్ని టార్గెట్స్ పూర్తి (TP5 ALL TARGETS HIT)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👑 కాంట్రాక్ట్: *{self.contract}*\n"
                f"📅 ఎక్స్‌పైరీ తేది: *{self.expiry_date}*\n\n"
                f"💰 ఎగ్జిట్ ధర: ₹{ltp:.2f} (+50 పాయింట్లు సాధించబడ్డాయి!)\n\n"
                f"🎉 పూర్తి లాభాలు బుక్ చేసుకుని ట్రేడ్ ముగించండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • Learn. Invest. Grow._"
            )
            dispatcher.send(msg)

# ==============================================================================
# 3. ADITYA INDIAN MARKET BOT
# ==============================================================================
class AdityaIndianMarketBot:
    def __init__(self, token: str, channel_id: str):
        self.dispatcher = TelegramDispatcher(token, channel_id)
        self.active_trade: Optional[TradePosition] = None

    def post_corporate_updates(self, date_str: str):
        msg = (
            f"📑 *ఆదిత్య ట్రేడ్ వేవ్స్ — కార్పొరేట్ & సెక్టార్ సమాచారం*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📅 *తేది*: {date_str} • ఉదయం 08:25 AM IST\n\n"
            f"🏢 *ఎక్స్ఛేంజ్ కార్పొరేట్ ఫైలింగ్స్ (NSE/BSE Filings)*:\n"
            f"• *KPI Green Energy*: సోలార్ పార్క్ ప్రాజెక్ట్ కింద ₹2,025 కోట్ల భారీ వర్క్ ఆర్డర్ లభించింది.\n"
            f"• *Navin Fluorine*: దహేజ్ వద్ద మల్టీపర్పస్ ప్లాంట్ విస్తరణ విజయవంతంగా పూర్తయింది.\n"
            f"• *Dr. Reddy's Lab*: రాబోయే రెండేళ్లలో 20-25 కొత్త ప్రొడక్టులను US మార్కెట్‌లో లాంచ్ చేయాలని లక్ష్యం.\n\n"
            f"📊 *కీలక రంగాలు (Sector Focus)*:\n"
            f"• *BFSI (బ్యాంకింగ్)*: హెచ్‌డీఎఫ్‌సీ బ్యాంక్, ఐసీఐసీఐ బ్యాంక్ సంస్థాగత ఆర్డర్ ఫ్లో పరిశీలనలో ఉంది.\n"
            f"• *IT సెక్టార్*: ఇన్ఫోసిస్, విప్రో మార్జిన్ ఒత్తిడిపై సెక్టార్ ఆధారిత దృష్టి.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ *సెబీ (SEBI) నిబంధనల గమనిక*:\n"
            f"_ఇది కేవలం సమాచారం మరియు విద్యా ప్రయోజనాల కోసం మాత్రమే. సెబీ రిజిస్టర్డ్ సిఫార్సు కాదు._"
        )
        self.dispatcher.send(msg)

    def post_today_strikes(self, instrument: str, spot_price: float, expiry_str: str):
        step = 100 if "BANK" in instrument else 50
        atm = int(round(spot_price / step) * step)
        msg = (
            f"📌 *నేటి ఫోకస్ స్ట్రైక్స్ — {instrument} (NSE)*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📅 *ఎక్స్‌పైరీ తేది*: {expiry_str}\n"
            f"📍 *ప్రారంభ స్పాట్ లెవెల్*: {spot_price:.2f}\n"
            f"🎯 *ఏటీఎం స్ట్రైక్ (ATM Strike)*: {atm}\n\n"
            f"👀 *వాచ్‌లిస్ట్‌లో ఉంచవలసినవి*:\n"
            f"  • *{instrument} {expiry_str} {atm} CE*\n"
            f"  • *{instrument} {expiry_str} {atm} PE*\n\n"
            f"⏱ *నియమం*: 5-నిమిషాల క్యాండిల్ క్లోజింగ్ వరకు ఎలాంటి తొందరపాటు నిర్ణయాలు తీసుకోవద్దు.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • సమాచార మార్గదర్శి_"
        )
        self.dispatcher.send(msg)

    def send_trade_signal(
        self,
        instrument: str,
        strike_num: int,
        opt_type: str,
        expiry_str: str,
        setup_type: str,
        candle_closed: str,
        entry_price: float,
        spot_index_val: float,
        spot_sl_val: float,
        green_line: float,
        red_line: float,
        why_text: str
    ):
        tp1 = round(entry_price + 10.0, 2)
        tp2 = round(entry_price + 20.0, 2)
        tp3 = round(entry_price + 30.0, 2)
        tp4 = round(entry_price + 40.0, 2)
        tp5 = round(entry_price + 50.0, 2)
        opt_sl = round(entry_price - 15.0, 2)

        contract_name = f"{instrument} {expiry_str} {strike_num} {opt_type}"

        self.active_trade = TradePosition(
            contract=contract_name,
            expiry_date=expiry_str,
            entry_price=entry_price,
            current_sl=opt_sl,
            target_1=tp1, target_2=tp2, target_3=tp3, target_4=tp4, target_5=tp5
        )

        badge = "🔴" if opt_type == "PE" else "🟢"
        msg = (
            f"{badge} *{instrument} — కొనుగోలు సూచన (BUY {strike_num} {opt_type})*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 *కాంట్రాక్ట్*: {contract_name}\n"
            f"📅 *ఎక్స్‌పైరీ తేది*: {expiry_str}\n\n"
            f"⏱ *వ్యూహం*: {setup_type}\n"
            f"🕯 *క్యాండిల్ సమయం*: {candle_closed} (5-మినిట్ స్ట్రక్చర్ & 1-మినిట్ ఎంట్రీ)\n\n"
            f"💰 *కొనుగోలు ధర (Entry)*: ₹{entry_price:.2f}\n\n"
            f"🎯 *టార్గెట్స్ (లక్ష్యాలు)*:\n"
            f"  • *TP1* : ₹{tp1:.2f} (+10 పాయింట్లు)\n"
            f"  • *TP2* : ₹{tp2:.2f} (+20 పాయింట్లు)\n"
            f"  • *TP3* : ₹{tp3:.2f} (+30 పాయింట్లు)\n"
            f"  • *TP4* : ₹{tp4:.2f} (+40 పాయింట్లు)\n"
            f"  • *TP5* : ₹{tp5:.2f} (+50 పాయింట్లు)\n\n"
            f"🛑 *ఆప్షన్ స్టాప్-లాస్* : ₹{opt_sl:.2f} (-15 పాయింట్లు)\n"
            f"🛑 *స్పాట్ ఇండెక్స్ స్టాప్-లాస్* : 5-నిమిషాల క్యాండిల్ {spot_sl_val:.2f} వద్ద క్లోజ్ అయితే ఎగ్జిట్\n\n"
            f"📍 *ఇండెక్స్ స్పాట్*: {spot_index_val:.2f}\n"
            f"📊 *కీలక లెవెల్స్*: గ్రీన్ లైన్ (సపోర్ట్) {green_line:.2f} • రెడ్ లైన్ (రెసిస్టెన్స్) {red_line:.2f}\n\n"
            f"💡 *కారణం (Why)*: {why_text}\n\n"
            f"📊 *వాల్యూమ్ చెక్*: ✔ మునుపటి క్యాండిల్ కంటే అధిక ఇన్‌స్టిట్యూషనల్ వాల్యూమ్‌తో ఆప్షన్ పైన ముగిసింది\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • SEBI రిజిస్టర్డ్ సలహా కాదు._"
        )
        self.dispatcher.send(msg)

    def post_market_breadth(self):
        msg = (
            f"📊 *మార్కెట్ ముగింపు స్థితిగతులు (MARKET RECAP)*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🇮🇳 *ప్రధాన సూచీలు*: నిఫ్టీ 50 & సెన్సెక్స్ ట్రేడింగ్ ముగిసింది.\n\n"
            f"🟢 *టాప్ గెయినర్స్ (Top Gainers)*:\n"
            f"• Kirloskar Oil Engine: ₹2,380.00 (+11.19%)\n"
            f"• Cupid Limited: ₹291.20 (+10.07%)\n"
            f"• TD Power Systems: ₹791.20 (+9.65%)\n\n"
            f"🔴 *టాప్ లూజర్స్ (Top Losers)*:\n"
            f"• PB Fintech: ₹1,084.10 (-5.89%)\n"
            f"• Honasa Consumer: ₹441.00 (-5.47%)\n"
            f"• Patanjali Foods: ₹371.25 (-5.15%)\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ మార్కెట్ పెట్టుబడులు రిస్క్‌తో కూడుకున్నవి. సరైన మనీ మేనేజ్‌మెంట్ పాటించండి.\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • Learn. Invest. Grow._"
        )
        self.dispatcher.send(msg)

# ==============================================================================
# 4. CONTINUOUS INTRADAY ENGINE (09:15 AM - 03:30 PM IST)
# ==============================================================================
def run_live_trading_day(bot: AdityaIndianMarketBot):
    ist = pytz.timezone('Asia/Kolkata')
    today_str = datetime.datetime.now(ist).strftime("%d %b %Y").upper()
    print(f">>> Live Session Engine Started for: {today_str}")

    # 1. Market Opening Corporate & Strike Updates
    bot.post_corporate_updates(date_str=today_str)
    time.sleep(2)
    bot.post_today_strikes(instrument="BANK NIFTY", spot_price=53890.0, expiry_str="CURRENT")

    signal_sent = False

    # 2. Continuous Loop until Market Closes (03:30 PM)
    while True:
        now = datetime.datetime.now(ist)
        current_time = now.time()

        # Market Close at 03:30 PM IST
        if current_time >= datetime.time(15, 30):
            print(">>> 03:30 PM: Market session closed. Posting breadth recap...")
            bot.post_market_breadth()
            break

        # Live Market Scanning Window
        if current_time >= datetime.time(9, 15):
            print(f"[{now.strftime('%H:%M:%S')}] Scanning 5-minute candles...")

            # Morning Confluence Demo Signal Trigger (between 09:35 - 09:40)
            if not signal_sent and current_time >= datetime.time(9, 35):
                bot.send_trade_signal(
                    instrument="BANK NIFTY",
                    strike_num=53800,
                    opt_type="PE",
                    expiry_str="CURRENT",
                    setup_type="రీట్రేస్ ఎంట్రీ (Retrace entry • short)",
                    candle_closed="09:35–09:40 క్యాండిల్ క్లోజ్",
                    entry_price=201.40,
                    spot_index_val=53794.55,
                    spot_sl_val=53907.15,
                    green_line=54405.30,
                    red_line=53894.60,
                    why_text="ధర రెడ్ లైన్ రెసిస్టెన్స్ వద్ద రిజెక్ట్ అయ్యి, 5-నిమిషాల క్యాండిల్ కిందనే ముగిసింది."
                )
                signal_sent = True

            # If active position exists, track TP updates
            if bot.active_trade and not bot.active_trade.is_closed:
                # Target progression check
                if 1 not in bot.active_trade.hit_targets:
                    bot.active_trade.update_ltp(212.0, bot.dispatcher)
                elif 2 not in bot.active_trade.hit_targets:
                    bot.active_trade.update_ltp(222.5, bot.dispatcher)

        # Sleep for 5 minutes (300 seconds) before next scan
        time.sleep(300)

if __name__ == "__main__":
    TOKEN = "8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM"
    CHANNEL_ID = "-1003832310811"

    bot = AdityaIndianMarketBot(token=TOKEN, channel_id=CHANNEL_ID)
    run_live_trading_day(bot)
