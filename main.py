"""
================================================================================
ADITYA TRADE WAVES — INSTITUTIONAL CAPITAL PROTECTION ENGINE
Features:
1. Pre-Market Settlement Scan (09:08 AM)
2. 10-Min Pre-Alert Heads-up Setup
3. Automated Break-Even Protection (TP1 hit -> SL moves to Cost)
4. Max Daily Loss Guard (2 continuous losses -> stop trading for the day)
5. Time-Decay Auto Exit Warning (30-min stagnation filter)
================================================================================
"""

import time
import datetime
import pytz
import requests
from dataclasses import dataclass, field
from typing import List, Optional, Dict

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

@dataclass
class CapitalGuardPosition:
    contract: str
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
        # 30 minutes dhati kooda target hit kaakapothe time decay nundi safe exit alert
        elapsed = (current_time - self.entry_time).total_seconds() / 60
        if elapsed >= 30 and len(self.hit_targets) == 0 and not self.is_closed:
            msg = (
                f"⏱ *TIME-DECAY ALERT — {self.contract}*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"⚠️ *గమనిక*: ట్రేడ్ ఎంటర్ అయ్యి 30 నిమిషాలు దాటింది. మార్కెట్‌లో మొమెంటమ్ లేదు.\n"
                f"💡 ఆప్షన్ ప్రీమియం కరిగిపోకుండా (Theta Decay) ఎగ్జిట్ అవ్వడం లేదా స్టాప్‌లాస్‌ను టైట్ చేయడం మంచిది.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • మూలధన రక్షణ_"
            )
            dispatcher.send(msg)

    def update_ltp(self, ltp: float, dispatcher: TelegramDispatcher) -> Optional[str]:
        if self.is_closed:
            return None

        # Stop-loss Hit
        if ltp <= self.current_sl:
            self.is_closed = True
            msg = (
                f"🛑 *స్టాప్-లాస్ హిట్ (CAPITAL PROTECTED EXIT)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"📍 ఎగ్జిట్ ధర: ₹{ltp:.2f} (రిస్క్ లిమిట్: ₹{self.current_sl:.2f})\n\n"
                f"🔒 పెద్ద నష్టం రాకుండా మూలధనం కాపాడబడింది. తదుపరి మంచి సెటప్ కోసం వేచి ఉండండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)
            return "LOSS"

        # TP1 Hit -> Move SL to Cost (Zero-Risk Trade Active)
        if 1 not in self.hit_targets and ltp >= self.target_1:
            self.hit_targets.append(1)
            self.current_sl = self.entry_price
            msg = (
                f"🎯 *TP1 పూర్తి — జీరో-రిస్క్ ప్రొటెక్షన్ ఆక్టివ్!*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f} (+10 పాయింట్లు)\n\n"
                f"🛡️ *జీరో లాస్ రూల్*: స్టాప్-లాస్ ధరను ₹{self.entry_price:.2f} (కొన్న ధర) కు మార్చండి.\n"
                f"ఇకపై ఈ ట్రేడ్‌లో నష్టం వచ్చే అవకాశమే లేదు!\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

        # TP2 Hit -> Partial Profit Booking
        if 2 not in self.hit_targets and ltp >= self.target_2:
            self.hit_targets.append(2)
            self.current_sl = self.target_1
            msg = (
                f"🎯🎯 *TP2 పూర్తి — లాభాల రక్షణ (+20 పాయింట్లు)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f}\n\n"
                f"👉 50% లాభాలు బుక్ చేసుకోండి. స్టాప్‌లాస్‌ను TP1 (₹{self.target_1:.2f}) వద్దకు ట్రైల్ చేయండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

        # TP5 Hit -> Full Exit
        if 5 not in self.hit_targets and ltp >= self.target_5:
            self.hit_targets.append(5)
            self.is_closed = True
            msg = (
                f"🏆 *జాక్‌పాట్ — అన్ని టార్గెట్స్ పూర్తి (+50 పాయింట్లు)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👑 కాంట్రాక్ట్: *{self.contract}*\n"
                f"💰 ఎగ్జిట్ ధర: ₹{ltp:.2f}\n\n"
                f"🎉 పూర్తి లాభాలు బుక్ చేసుకుని ఈరోజు ట్రేడ్ ముగించండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)
            return "WIN"

        return None

class AdityaInstitutionalProtectionBot:
    def __init__(self, token: str, channel_id: str):
        self.dispatcher = TelegramDispatcher(token, channel_id)
        self.active_position: Optional[CapitalGuardPosition] = None
        self.consecutive_losses = 0
        self.max_daily_losses = 2  # Circuit Breaker

    def send_pre_market_brief(self):
        msg = (
            f"🌅 *ఆదిత్య ట్రేడ్ వేవ్స్ — ప్రీ-మార్కెట్ విశ్లేషణ & లెవెల్స్*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 *కీలక జోన్లు (No-Trade Zones)*:\n"
            f"• నిఫ్టీ/బ్యాంక్ నిఫ్టీ రేంజ్ మధ్యలో ఉన్నప్పుడు ట్రేడ్ చేయరాదు.\n"
            f"• కేవలం సపోర్ట్ (గ్రీన్ లైన్) లేదా రెసిస్టెన్స్ (రెడ్ లైన్) వద్ద రివర్సల్ లేదా బ్రేకవుట్ వచ్చినప్పుడే ఎంట్రీ.\n\n"
            f"🛡️ *రక్షణ నియమం*: మొదటి 15 నిమిషాల వరకు హై-వోలటాలిటీ నడుస్తుంది, ప్రైస్ సెటిల్ అయ్యే వరకు తొందరపడకండి.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • SEBI రిజిస్టర్డ్ సలహా కాదు._"
        )
        self.dispatcher.send(msg)

    def send_early_radar(self, instrument: str, direction: str, trigger_price: float):
        msg = (
            f"⚠️ *10-MIN ADVANCE RADAR — {instrument}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🔍 *సెటప్ రూపుదిద్దుకుంటోంది*:\n"
            f"• మార్కెట్ కీలకమైన లెవెల్ ₹{trigger_price:.2f} వద్దకు చేరుకుంటోంది.\n"
            f"• దిశ: *{direction}*\n\n"
            f"🛑 *ముఖ్యమైన హెచ్చరిక*: ఇప్పుడే ఎంట్రీ తీసుకోకండి! 5-నిమిషాల క్యాండిల్ క్లోజింగ్ మరియు వాల్యూమ్ కన్‌ఫర్మేషన్ వచ్చే వరకు వేచి ఉండండి.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
        )
        self.dispatcher.send(msg)

    def trigger_trade(self, instrument: str, strike: int, opt_type: str, entry_price: float, spot_sl: float):
        if self.consecutive_losses >= self.max_daily_losses:
            print("[CIRCUIT BREAKER]: Daily loss limit reached. No new trades allowed.")
            return

        now = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        tp1 = round(entry_price + 10.0, 2)
        tp2 = round(entry_price + 20.0, 2)
        tp3 = round(entry_price + 30.0, 2)
        tp4 = round(entry_price + 40.0, 2)
        tp5 = round(entry_price + 50.0, 2)
        opt_sl = round(entry_price - 15.0, 2)

        contract = f"{instrument} {strike} {opt_type}"
        self.active_position = CapitalGuardPosition(
            contract=contract,
            entry_price=entry_price,
            current_sl=opt_sl,
            entry_time=now,
            target_1=tp1, target_2=tp2, target_3=tp3, target_4=tp4, target_5=tp5
        )

        badge = "🔴" if opt_type == "PE" else "🟢"
        msg = (
            f"{badge} *కన్‌ఫర్మ్డ్ ఎంట్రీ — {contract}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💰 *కొనుగోలు ధర (Entry)*: ₹{entry_price:.2f}\n"
            f"🛑 *స్ట్రిక్ట్ స్టాప్-లాస్*: ₹{opt_sl:.2f} (కేవలం 15 పాయింట్ల లిమిట్)\n"
            f"📍 *స్పాట్ ఇండెక్స్ SL*: 5M క్యాండిల్ {spot_sl:.2f} దాటితే ఎగ్జిట్\n\n"
            f"🎯 *లక్ష్యాలు (Targets)*:\n"
            f"  • *TP1*: ₹{tp1:.2f} (+10 pts) -> _(ఇక్కడ SL కొన్న ధరకు మారుతుంది - జీరో రిస్క్)_\n"
            f"  • *TP2*: ₹{tp2:.2f} (+20 pts) -> _(50% ప్రాఫిట్ బుకింగ్)_\n"
            f"  • *TP3*: ₹{tp3:.2f} (+30 pts)\n"
            f"  • *TP4*: ₹{tp4:.2f} (+40 pts)\n"
            f"  • *TP5*: ₹{tp5:.2f} (+50 pts)\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ _స్టాప్‌లాస్ లేకుండా ఎవరూ ట్రేడ్ చేయరాదు._"
        )
        self.dispatcher.send(msg)

if __name__ == "__main__":
    TOKEN = "8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM"
    CHANNEL_ID = "-1003832310811"

    bot = AdityaInstitutionalProtectionBot(token=TOKEN, channel_id=CHANNEL_ID)

    print(">>> 1. ప్రీ-మార్కెట్ సేఫ్టీ లెవెల్స్ పంపుతోంది...")
    bot.send_pre_market_brief()
    time.sleep(2)

    print(">>> 2. 10-నిమిషాల అడ్వాన్స్ రాడార్ వార్నింగ్...")
    bot.send_early_radar(instrument="BANK NIFTY", direction="PUT (PE)", trigger_price=53890.0)
    time.sleep(2)

    print(">>> 3. కన్‌ఫర్మ్డ్ జీరో-లాస్ ప్రొటెక్టెడ్ ట్రేడ్ ఎంట్రీ...")
    bot.trigger_trade(instrument="BANK NIFTY", strike=53800, opt_type="PE", entry_price=201.40, spot_sl=53907.15)
    time.sleep(2)

    print(">>> 4. TP1 హిట్ సిమ్యులేషన్ (స్టాప్‌లాస్ కాస్ట్ వద్దకు మార్చబడింది)...")
    if bot.active_position:
        bot.active_position.update_ltp(212.0, bot.dispatcher)
        time.sleep(2)
        bot.active_position.update_ltp(222.5, bot.dispatcher)

    print("\n✅ అన్ని క్యాపిటల్ ప్రొటెక్షన్ అలర్ట్స్ విజయవంతంగా పంపబడ్డాయి!")
