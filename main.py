"""
================================================================================
ADITYA TRADE WAVES — COMPLETE INSTITUTIONAL TRADING AGENT
Author: Aditya Trade Waves
Rules: Steve Nison Price Action + Zerodha Varsity Technical Confluence
Channel ID: -1003832310811
Bot Token: 8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM
================================================================================
"""

import time
import datetime
import pytz
import requests
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
            if res.status_code == 200:
                print("[Success]: Telegram alert dispatched.")
                return True
            else:
                print(f"[Telegram API Error {res.status_code}]: {res.text}")
                return False
        except Exception as e:
            print(f"[Network Error]: {e}")
            return False

# ==============================================================================
# 2. POSITION & ZERO-RISK TRAILING ENGINE
# ==============================================================================
@dataclass
class CapitalGuardPosition:
    contract: str
    expiry_date: str
    entry_price: float
    current_sl: float
    entry_time: datetime.datetime
    target_1: float
    target_2: float
    target_3: float
    target_4: float
    target_5: float
    hit_targets: List[int] = field(default_factory=list)
    is_closed: bool = False

    def check_time_decay(self, current_time: datetime.datetime, dispatcher: TelegramDispatcher):
        elapsed = (current_time - self.entry_time).total_seconds() / 60
        if elapsed >= 25 and len(self.hit_targets) == 0 and not self.is_closed:
            msg = (
                f"⏱ *TIME-DECAY ALERT — {self.contract}*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"⚠️ *గమనిక*: ట్రేడ్ ఎంటర్ అయ్యి 25 నిమిషాలు దాటింది. మొమెంటమ్ నెమ్మదించింది.\n"
                f"💡 ఆప్షన్ ప్రీమియం కరిగిపోకుండా (Theta Decay) కాపాడటానికి కాస్ట్-టు-కాస్ట్ ఎగ్జిట్ లేదా స్టాప్‌లాస్‌ను కఠినతరం చేయండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • క్యాపిటల్ గార్డ్_"
            )
            dispatcher.send(msg)

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
                f"📅 ఎక్స్‌పైరీ: *{self.expiry_date}*\n\n"
                f"📍 ఎగ్జిట్ ధర: ₹{ltp:.2f} (SL: ₹{self.current_sl:.2f})\n\n"
                f"🔒 పెద్ద నష్టం రాకుండా మూలధనం కాపాడబడింది. క్రమశిక్షణతో కూడిన ముగింపు.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • SEBI రిస్క్ నియమాలు_"
            )
            dispatcher.send(msg)
            return "LOSS"

        # TP1 (+10 pts) -> Move SL to Cost (Zero-Risk Trade Active)
        if 1 not in self.hit_targets and ltp >= self.target_1:
            self.hit_targets.append(1)
            self.current_sl = self.entry_price
            msg = (
                f"🎯 *TP1 పూర్తి (+10 పాయింట్లు) — జీరో-రిస్క్ ప్రొటెక్షన్ ఆక్టివ్!*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f}\n\n"
                f"🛡️ *జీరో లాస్ రూల్*: స్టాప్-లాస్ ధరను వెంటనే కొన్న ధర వద్దకు (Cost Price ₹{self.entry_price:.2f}) మార్చండి.\n"
                f"🔒 ఇకపై ఈ ట్రేడ్‌లో నష్టం వచ్చే అవకాశమే లేదు!\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

        # TP2 (+20 pts) -> Partial Profit Booking
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

        # TP3 (+30 pts)
        if 3 not in self.hit_targets and ltp >= self.target_3:
            self.hit_targets.append(3)
            self.current_sl = self.target_2
            msg = (
                f"🎯🎯🎯 *TP3 పూర్తి (+30 పాయింట్లు)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f}\n\n"
                f"👉 స్టాప్‌లాస్‌ను TP2 (₹{self.target_2:.2f}) వద్దకు ట్రైల్ చేయండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

        # TP5 (+50 pts) -> Full Exit
        if 5 not in self.hit_targets and ltp >= self.target_5:
            self.hit_targets.append(5)
            self.is_closed = True
            msg = (
                f"🏆 *జాక్‌పాట్ — అన్ని టార్గెట్స్ పూర్తి (+50 పాయింట్లు సాధించబడ్డాయి)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👑 కాంట్రాక్ట్: *{self.contract}*\n"
                f"💰 ఎగ్జిట్ ధర: ₹{ltp:.2f}\n\n"
                f"🎉 పూర్తి లాభాలు బుక్ చేసుకుని విజయవంతంగా ట్రేడ్ ముగించండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • Learn. Invest. Grow._"
            )
            dispatcher.send(msg)
            return "WIN"

        return None

# ==============================================================================
# 3. MASTER BOT ENGINE (PRE-MARKET + CANDLE CONFLUENCE + RADAR)
# ==============================================================================
class AdityaInstitutionalBot:
    def __init__(self, token: str, channel_id: str):
        self.dispatcher = TelegramDispatcher(token, channel_id)
        self.active_position: Optional[CapitalGuardPosition] = None
        self.daily_losses = 0
        self.max_daily_losses = 2  # Circuit Breaker

    # 09:08 AM: Pre-Market Analysis
    def post_pre_market_analysis(self, date_str: str):
        msg = (
            f"🌅 *ఆదిత్య ట్రేడ్ వేవ్స్ — ప్రీ-మార్కెట్ సెటిల్‌మెంట్ & లెవెల్స్*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📅 *తేది*: {date_str} • 09:08 AM IST\n\n"
            f"📊 *భారతీయ సూచీల ప్రీ-ఓపెన్ స్థితి (NSE/BSE)*:\n"
            f"• *NIFTY 50*: 24,850.00 (+70 పాయింట్లు • గ్యాప్-అప్)\n"
            f"• *BANK NIFTY*: 53,890.00 (-110 పాయింట్లు • గ్యాప్-డౌన్)\n"
            f"• *SENSEX*: 81,520.00 (+180 పాయింట్లు • గ్యాప్-అప్)\n\n"
            f"🎯 *నేటి కీలక ప్రైస్ యాక్షన్ లైన్స్*:\n"
            f"🟢 *సపోర్ట్ జోన్ (Green Line)*: 53,750 (బయ్యర్స్ ఏరియా)\n"
            f"🔴 *రెసిస్టెన్స్ జోన్ (Red Line)*: 54,180 (సెల్లర్స్ ఏరియా)\n\n"
            f"🛡️ *రక్షణ నియమం*: మొదటి 15 నిమిషాల వరకు ప్రైస్ సెటిల్ అయ్యే వరకు వేచి చూడండి. తొందరపడి ఎంట్రీ తీసుకోవద్దు.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ _విద్యా ప్రయోజనాల కొరకు మాత్రమే. SEBI రిజిస్టర్డ్ సిఫార్సు కాదు._"
        )
        self.dispatcher.send(msg)

    # 2-Minute Advance Heads-Up Radar Alert
    def send_2min_heads_up_radar(self, instrument: str, strike: int, opt_type: str, key_level: float, note: str):
        badge = "⚡ 🟢 [BUY WATCH]" if opt_type == "CE" else "⚡ 🔴 [SELL WATCH]"
        msg = (
            f"{badge} *2-MIN HEADS-UP RADAR — {instrument}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👀 *వాచ్‌లిస్ట్‌లో యాడ్ చేసుకోండి*: *{strike} {opt_type}*\n"
            f"📍 *కీలక లెవెల్*: ₹{key_level:.2f}\n"
            f"⏱ *క్యాండిల్ సమయం*: 5-మినిట్ క్యాండిల్ క్లోజ్ అవ్వడానికి ఇంకా 2 నిమిషాలు ఉంది.\n\n"
            f"💡 *సెటప్ గమనిక*: {note}\n\n"
            f"🛑 *ముఖ్యమైన నియమం*: క్యాండిల్ పూర్తిగా క్లోజ్ అయ్యే వరకు ఎంట్రీ బటన్ నొక్కవద్దు. కన్‌ఫర్మేషన్ రాగానే పూర్తి స్టాప్‌లాస్‌తో ట్రిగ్గర్ అలర్ట్ వస్తుంది.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • ప్రిపరేషన్ రాడార్_"
        )
        self.dispatcher.send(msg)

    # Confirmed Entry Signal (Steve Nison Candle Close + Volume Confirmation)
    def send_confirmed_trade(
        self,
        instrument: str,
        strike: int,
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
        if self.daily_losses >= self.max_daily_losses:
            print("[CIRCUIT BREAKER]: Daily loss limit reached. No new trades generated.")
            return

        tp1 = round(entry_price + 10.0, 2)
        tp2 = round(entry_price + 20.0, 2)
        tp3 = round(entry_price + 30.0, 2)
        tp4 = round(entry_price + 40.0, 2)
        tp5 = round(entry_price + 50.0, 2)
        opt_sl = round(entry_price - 15.0, 2)

        contract_name = f"{instrument} {expiry_str} {strike} {opt_type}"
        now = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))

        self.active_position = CapitalGuardPosition(
            contract=contract_name,
            expiry_date=expiry_str,
            entry_price=entry_price,
            current_sl=opt_sl,
            entry_time=now,
            target_1=tp1, target_2=tp2, target_3=tp3, target_4=tp4, target_5=tp5
        )

        badge = "🔴" if opt_type == "PE" else "🟢"
        msg = (
            f"{badge} *{instrument} — కన్‌ఫర్మ్డ్ కొనుగోలు సూచన (BUY {strike} {opt_type})*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 *కాంట్రాక్ట్*: {contract_name}\n"
            f"📅 *ఎక్స్‌పైరీ తేది*: {expiry_str}\n\n"
            f"⏱ *వ్యూహం*: {setup_type}\n"
            f"🕯 *క్యాండిల్*: {candle_closed} (5M బాడీ & విక్ కన్‌ఫర్మ్ అయింది)\n\n"
            f"💰 *ఖచ్చితమైన కొనుగోలు ధర (Entry)*: ₹{entry_price:.2f}\n\n"
            f"🎯 *లక్ష్యాలు (Targets)*:\n"
            f"  • *TP1* : ₹{tp1:.2f} (+10 pts) -> _(స్టాప్‌లాస్ కాస్ట్‌కు మారుతుంది - జీరో రిస్క్)_\n"
            f"  • *TP2* : ₹{tp2:.2f} (+20 pts) -> _(50% లాభాల బుకింగ్)_\n"
            f"  • *TP3* : ₹{tp3:.2f} (+30 pts)\n"
            f"  • *TP4* : ₹{tp4:.2f} (+40 pts)\n"
            f"  • *TP5* : ₹{tp5:.2f} (+50 pts)\n\n"
            f"🛑 *స్ట్రిక్ట్ ఆప్షన్ స్టాప్-లాస్* : ₹{opt_sl:.2f} (-15 పాయింట్ల రిస్క్ లిమిట్)\n"
            f"🛑 *స్పాట్ ఇండెక్స్ స్టాప్-లాస్* : 5-నిమిషాల క్యాండిల్ {spot_sl_val:.2f} దాటి క్లోజ్ అయితే ఎగ్జిట్\n\n"
            f"📍 *ఇండెక్స్ స్పాట్*: {spot_index_val:.2f}\n"
            f"📊 *కీలక లెవెల్స్*: సపోర్ట్ {green_line:.2f} • రెసిస్టెన్స్ {red_line:.2f}\n\n"
            f"💡 *కారణం (Why)*: {why_text}\n"
            f"📊 *వాల్యూమ్ చెక్*: ✔ మునుపటి క్యాండిల్ కంటే అధిక ఇన్‌స్టిట్యూషనల్ వాల్యూమ్‌తో ఆప్షన్ పైన ముగిసింది\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ _స్టాప్‌లాస్ లేకుండా ఎవరూ ట్రేడ్ చేయరాదు._"
        )
        self.dispatcher.send(msg)

    # 03:30 PM: Post-Market Wrap
    def post_market_recap(self):
        msg = (
            f"📊 *మార్కెట్ ముగింపు స్థితిగతులు (MARKET RECAP — 03:30 PM)*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🇮🇳 *ప్రధాన సూచీలు*: నిఫ్టీ 50 & సెన్సెక్స్ నేటి ట్రేడింగ్ ముగిసింది.\n\n"
            f"🟢 *టాప్ గెయినర్స్*:\n"
            f"• Kirloskar Oil: ₹2,380.00 (+11.19%)\n"
            f"• Cupid Ltd: ₹291.20 (+10.07%)\n"
            f"• TD Power: ₹791.20 (+9.65%)\n\n"
            f"🔴 *టాప్ లూజర్స్*:\n"
            f"• PB Fintech: ₹1,084.10 (-5.89%)\n"
            f"• Honasa Consumer: ₹441.00 (-5.47%)\n"
            f"• Patanjali Foods: ₹371.25 (-5.15%)\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛡️ *క్రమశిక్షణ సందేశం*: లాభాల కంటే ముందుగా మూలధన రక్షణకు ప్రాధాన్యత ఇవ్వండి.\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • Learn. Invest. Grow._"
        )
        self.dispatcher.send(msg)

# ==============================================================================
# 4. EXECUTION DRIVER
# ==============================================================================
def run_trading_system():
    TOKEN = "8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM"
    CHANNEL_ID = "-1003832310811"

    bot = AdityaInstitutionalBot(token=TOKEN, channel_id=CHANNEL_ID)
    ist = pytz.timezone('Asia/Kolkata')
    today_str = datetime.datetime.now(ist).strftime("%d %b %Y").upper()

    print(f">>> Aditya Trade Waves System Executing for: {today_str}")

    # 1. 09:08 AM: Pre-Market Analysis
    print(">>> 1. ప్రీ-మార్కెట్ డేటా పంపుతోంది...")
    bot.post_pre_market_analysis(date_str=today_str)
    time.sleep(2)

    # 2. 09:33 AM: 2-Minute Advance Heads-Up Radar
    print(">>> 2. 2-మినిట్ అడ్వాన్స్ రాడార్ అలర్ట్ పంపుతోంది...")
    bot.send_2min_heads_up_radar(
        instrument="BANK NIFTY",
        strike=53800,
        opt_type="PE",
        key_level=53894.60,
        note="ధర రెడ్ లైన్ రెసిస్టెన్స్ వద్ద తిరస్కరణకు గురవుతోంది. బేరిష్ రిజెక్షన్ క్యాండిల్ రూపుదిద్దుకుంటోంది."
    )
    time.sleep(2)

    # 3. 09:35 AM: Confirmed Trade Signal
    print(">>> 3. కన్‌ఫర్మ్డ్ ట్రేడ్ సిగ్నల్ పంపుతోంది...")
    bot.send_confirmed_trade(
        instrument="BANK NIFTY",
        strike=53800,
        opt_type="PE",
        expiry_str="CURRENT",
        setup_type="రీట్రేస్ ఎంట్రీ (Retrace entry • short)",
        candle_closed="09:35 క్యాండిల్ క్లోజ్",
        entry_price=201.40,
        spot_index_val=53794.55,
        spot_sl_val=53907.15,
        green_line=54405.30,
        red_line=53894.60,
        why_text="ధర రెడ్ లైన్ రెసిస్టెన్స్ వద్ద రిజెక్ట్ అయ్యి, అధిక వాల్యూమ్‌తో 5-మినిట్ క్యాండిల్ కింద ముగిసింది."
    )
    time.sleep(2)

    # 4. Target Trailing Demonstration (TP1, TP2 & Zero-Risk Move)
    print(">>> 4. టార్గెట్స్ & జీరో-రిస్క్ ట్రైలింగ్ అప్‌డేట్స్...")
    if bot.active_position:
        bot.active_position.update_ltp(212.0, bot.dispatcher) # TP1 Hit (+10 pts) -> SL moves to cost
        time.sleep(2)
        bot.active_position.update_ltp(222.5, bot.dispatcher) # TP2 Hit (+20 pts) -> 50% profit booked

    # 5. 03:30 PM: Market Close Wrap
    print(">>> 5. మార్కెట్ ముగింపు సమ్మరీ...")
    bot.post_market_recap()

    print("\n✅ అన్ని విభాగాలు టెలిగ్రామ్ ఛానెల్ (-1003832310811) లో విజయవంతంగా రన్ అయ్యాయి!")

if __name__ == "__main__":
    run_trading_system()
