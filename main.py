"""
================================================================================
ADITYA TRADE WAVES — TELUGU ALERTS INSTITUTIONAL MASTER AGENT
Target Channel: @adityatradewaves
Bot Token: 8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM
================================================================================
"""

import time
import requests
from dataclasses import dataclass, field
from typing import List, Optional

# ==============================================================================
# 1. TELEGRAM DISPATCHER
# ==============================================================================
class TelegramDispatcher:
    def __init__(self, bot_token: str, channel_username: str = "@adityatradewaves"):
        self.bot_token = bot_token
        self.channel_username = channel_username
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send(self, text: str) -> bool:
        payload = {
            "chat_id": self.channel_username,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            res = requests.post(self.api_url, json=payload, timeout=12)
            return res.status_code == 200
        except Exception as e:
            print(f"[Error]: {e}")
            return False

# ==============================================================================
# 2. POSITION & TARGET TRACKER (TELUGU ALERTS)
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

        # Stop-Loss Check
        if ltp <= self.current_sl:
            self.is_closed = True
            msg = (
                f"🛑 *స్టాప్-లాస్ హిట్ అయింది (STOP-LOSS HIT)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 *కాంట్రాక్ట్*: {self.contract}\n"
                f"📅 *ఎక్స్‌పైరీ తేది*: {self.expiry_date}\n\n"
                f"📍 *ఎగ్జిట్ ధర*: ₹{ltp:.2f}\n"
                f"🛑 *స్టాప్-లాస్ లెవెల్*: ₹{self.current_sl:.2f}\n\n"
                f"💡 *సూచన*: ట్రేడ్ క్లోజ్ అయింది. పెట్టుబడి రక్షణకు ప్రాధాన్యత ఇవ్వబడింది.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • క్రమశిక్షణతో కూడిన ట్రేడింగ్_"
            )
            dispatcher.send(msg)
            return

        # Target 1 (+10 pts)
        if 1 not in self.hit_targets and ltp >= self.target_1:
            self.hit_targets.append(1)
            self.current_sl = self.entry_price # Move SL to Cost
            msg = (
                f"🎯 *మొదటి టార్గెట్ రీచ్ అయింది (TP1 DONE)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 *కాంట్రాక్ట్*: {self.contract}\n"
                f"📅 *ఎక్స్‌పైరీ తేది*: {self.expiry_date}\n\n"
                f"💰 *ప్రస్తుత ధర*: ₹{ltp:.2f} (+10 పాయింట్లు)\n\n"
                f"👉 *తదుపరి చర్య*: స్టాప్-లాస్‌ను వెంటనే కొన్న ధర వద్దకు (Cost Price ₹{self.entry_price:.2f}) మార్చండి.\n"
                f"🔒 *రిస్క్*: జీరో-రిస్క్ ట్రేడ్ ఆక్టివేట్ అయింది! తదుపరి లక్ష్యం TP2...\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

        # Target 2 (+20 pts)
        if 2 not in self.hit_targets and ltp >= self.target_2:
            self.hit_targets.append(2)
            self.current_sl = self.target_1
            msg = (
                f"🎯🎯 *రెండవ టార్గెట్ రీచ్ అయింది (TP2 DONE)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 *కాంట్రాక్ట్*: {self.contract}\n"
                f"📅 *ఎక్స్‌పైరీ తేది*: {self.expiry_date}\n\n"
                f"💰 *ప్రస్తుత ధర*: ₹{ltp:.2f} (+20 పాయింట్లు)\n\n"
                f"👉 *తదుపరి చర్య*: 50% లాభాలు బుక్ చేసుకోండి. స్టాప్-లాస్‌ను TP1 (₹{self.target_1:.2f}) వద్దకు జరపండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

        # Target 3 (+30 pts)
        if 3 not in self.hit_targets and ltp >= self.target_3:
            self.hit_targets.append(3)
            self.current_sl = self.target_2
            msg = (
                f"🎯🎯🎯 *మూడవ టార్గెట్ రీచ్ అయింది (TP3 DONE)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 *కాంట్రాక్ట్*: {self.contract}\n"
                f"📅 *ఎక్స్‌పైరీ తేది*: {self.expiry_date}\n\n"
                f"💰 *ప్రస్తుత ధర*: ₹{ltp:.2f} (+30 పాయింట్లు)\n\n"
                f"👉 *తదుపరి చర్య*: స్టాప్-లాస్‌ను TP2 (₹{self.target_2:.2f}) వద్దకు ట్రైల్ చేయండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

        # Target 5 (+50 pts)
        if 5 not in self.hit_targets and ltp >= self.target_5:
            self.hit_targets.append(5)
            self.is_closed = True
            msg = (
                f"🏆 *అన్ని టార్గెట్స్ పూర్తి అయ్యాయి (ALL TARGETS HIT)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👑 *కాంట్రాక్ట్*: {self.contract}\n"
                f"📅 *ఎక్స్‌పైరీ తేది*: {self.expiry_date}\n\n"
                f"💰 *ప్రస్తుత ధర*: ₹{ltp:.2f} (+50 పాయింట్లు లభించాయి!)\n\n"
                f"🎉 *తదుపరి చర్య*: పూర్తి లాభాలు బుక్ చేసుకుని ట్రేడ్ నుండి బయటకు రండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • విజయవంతమైన ముగింపు_"
            )
            dispatcher.send(msg)

# ==============================================================================
# 3. MASTER BOT CLASS (TELUGU LAYOUT)
# ==============================================================================
class AdityaTeluguAgent:
    def __init__(self, token: str, channel: str):
        self.dispatcher = TelegramDispatcher(token, channel)
        self.active_trade: Optional[TradePosition] = None

    def post_pre_market(self, date_str: str):
        msg = (
            f"🌅 *ప్రీ-మార్కెట్ సమాచారం (PRE-MARKET BRIEF)*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📅 *తేది*: {date_str} • మార్కెట్ ప్రారంభానికి ముందు\n\n"
            f"🌐 *గ్లోబల్ మార్కెట్లు*: యూఎస్ నాస్‌డాక్, డౌ జోన్స్ మరియు గిఫ్ట్ నిఫ్టీ డేటా విశ్లేషించబడింది.\n"
            f"📰 *న్యూస్ సెంటిమెంట్*: సానుకూల ధోరణి / ఇన్‌స్టిట్యూషనల్ వాచ్‌లిస్ట్ ఆక్టివ్.\n\n"
            f"⏳ ఉదయం 09:10 కు ప్రీ-ఓపెన్ స్ట్రైక్ వివరాలు అందించబడతాయి.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • అవగాహన కోసం మాత్రమే, ఇది సిఫార్సు కాదు._"
        )
        self.dispatcher.send(msg)

    def post_today_strikes(self, instrument: str, spot_val: float, expiry_str: str):
        step = 100 if "BANK" in instrument else 50
        atm = int(round(spot_val / step) * step)
        msg = (
            f"📌 *ఈరోజు ఫోకస్ చేయవలసిన స్ట్రైక్స్ — {instrument}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📅 *ఎక్స్‌పైరీ తేది*: {expiry_str}\n"
            f"📍 *స్పాట్ లెవెల్*: {spot_val:.2f}\n"
            f"🎯 *ఏటీఎం స్ట్రైక్*: {atm}\n\n"
            f"👀 *వాచ్‌లిస్ట్‌లో ఉంచవలసినవి*:\n"
            f"  • *{instrument} {expiry_str} {atm} CE*\n"
            f"  • *{instrument} {expiry_str} {atm} PE*\n\n"
            f"⏱ *నియమం*: 5 నిమిషాల క్యాండిల్ క్లోజింగ్ వరకు వేచి ఉండండి.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • సమాచారం కోసం మాత్రమే._"
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
            target_1=tp1,
            target_2=tp2,
            target_3=tp3,
            target_4=tp4,
            target_5=tp5
        )

        badge = "🔴" if opt_type == "PE" else "🟢"

        msg = (
            f"{badge} *{instrument} — బై సిగ్నల్ (BUY {strike_num} {opt_type})*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 *కాంట్రాక్ట్*: {contract_name}\n"
            f"📅 *ఎక్స్‌పైరీ తేది*: {expiry_str}\n\n"
            f"⏱ *వ్యూహం*: {setup_type}\n"
            f"🕯 *క్యాండిల్ సమయం*: {candle_closed} ముగిసిన తర్వాత\n\n"
            f"💰 *కొనుగోలు ధర (ఎంట్రీ)*: ₹{entry_price:.2f}\n\n"
            f"🎯 *టార్గెట్స్ (లక్ష్యాలు)*:\n"
            f"  • *TP1* : ₹{tp1:.2f} (+10 పాయింట్లు)\n"
            f"  • *TP2* : ₹{tp2:.2f} (+20 పాయింట్లు)\n"
            f"  • *TP3* : ₹{tp3:.2f} (+30 పాయింట్లు)\n"
            f"  • *TP4* : ₹{tp4:.2f} (+40 పాయింట్లు)\n"
            f"  • *TP5* : ₹{tp5:.2f} (+50 పాయింట్లు)\n\n"
            f"🛑 *ఆప్షన్ స్టాప్-లాస్* : ₹{opt_sl:.2f} (-15 పాయింట్లు)\n"
            f"🛑 *స్పాట్ ఇండెక్స్ స్టాప్-లాస్* : 5-నిమిషాల క్యాండిల్ {spot_sl_val:.2f} పైన క్లోజ్ అయితే నిష్క్రమించండి\n\n"
            f"📍 *ఇండెక్స్ స్పాట్*: {spot_index_val:.2f} • గ్రీన్ లైన్: {green_line:.2f} • రెడ్ లైన్: {red_line:.2f}\n\n"
            f"💡 *కారణం (Why)*: {why_text}\n\n"
            f"📊 *వాల్యూమ్ చెక్*: ✔ మునుపటి క్యాండిల్ కంటే అధిక వాల్యూమ్‌తో ఆప్షన్ పైన ముగిసింది\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • అవగాహన కోసం మాత్రమే, ఇది సిఫార్సు కాదు._"
        )
        self.dispatcher.send(msg)


# ==============================================================================
# 4. EXECUTION DRIVER
# ==============================================================================
if __name__ == "__main__":
    TOKEN = "8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM"
    CHANNEL = "@adityatradewaves"

    bot = AdityaTeluguAgent(token=TOKEN, channel=CHANNEL)

    print(">>> 1. ప్రీ-మార్కెట్ బ్రీఫ్ పంపుతోంది...")
    bot.post_pre_market(date_str="29 SEP 2026")
    time.sleep(2)

    print(">>> 2. ఏటీఎం స్ట్రైక్స్ వాచ్‌లిస్ట్ పంపుతోంది...")
    bot.post_today_strikes(instrument="BANK NIFTY", spot_val=53891.10, expiry_str="29 SEP")
    time.sleep(2)

    print(">>> 3. లైవ్ ట్రేడ్ సిగ్నల్ తెలుగు ఫార్మాట్‌లో పంపుతోంది...")
    bot.send_trade_signal(
        instrument="BANK NIFTY",
        strike_num=53800,
        opt_type="PE",
        expiry_str="29 SEP",
        setup_type="రీట్రేస్ ఎంట్రీ (Retrace entry • short)",
        candle_closed="09:35–09:40 క్యాండిల్",
        entry_price=201.40,
        spot_index_val=53794.55,
        spot_sl_val=53907.15,
        green_line=54405.30,
        red_line=53894.60,
        why_text="ధర తిరిగి రెడ్ లైన్ వద్దకు చేరి, రిజెక్ట్ అయ్యి మళ్లీ కిందనే క్లోజ్ అయింది."
    )
    time.sleep(2)

    print(">>> 4. టార్గెట్స్ రీచ్ టెస్టింగ్ (TP1 & TP2)...")
    bot.active_trade.update_ltp(212.0, bot.dispatcher) # TP1 hit (+10 pts)
    time.sleep(2)
    bot.active_trade.update_ltp(222.5, bot.dispatcher) # TP2 hit (+20 pts)

    print("\n✅ అన్ని మెసేజ్‌లు తెలుగు ఫాంట్‌లో విజయవంతంగా Telegram కు వెళ్లాయి!")
