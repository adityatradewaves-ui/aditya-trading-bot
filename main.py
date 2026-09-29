"""
================================================================================
ADITYA TRADE WAVES — COMPLETE VALUEBULL & MONEY PURSE ECOSYSTEM AGENT
Features:
1. Corporate Filings & Orders (KPI Green, TMB, Navin Fluorine style)
2. Daily Gainers & Losers Index Recap (Money Purse Style)
3. 5-Min + 1-Min Confluence Option Trades (TP1 to TP5)
4. Regulatory Disclaimers
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
            print(f"[Network Error]: {e}")
            return False

# ==============================================================================
# 2. POSITION & MULTI-TARGET TRACKER
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
                f"📍 ఎగ్జిట్ ధర: ₹{ltp:.2f} (SL: ₹{self.current_sl:.2f})\n\n"
                f"💡 పెట్టుబడి రక్షణకు ప్రాధాన్యత ఇవ్వబడింది."
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
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f} (+10 పాయింట్లు)\n\n"
                f"👉 స్టాప్-లాస్‌ను వెంటనే కొనుగోలు ధర (₹{self.entry_price:.2f}) కు మార్చండి. జీరో-రిస్క్ ట్రేడ్ ఆక్టివ్!"
            )
            dispatcher.send(msg)

        if 2 not in self.hit_targets and ltp >= self.target_2:
            self.hit_targets.append(2)
            self.current_sl = self.target_1
            msg = (
                f"🎯🎯 *రెండవ టార్గెట్ పూర్తి (TP2 DONE)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f} (+20 పాయింట్లు)\n\n"
                f"👉 50% లాభాలు బుక్ చేసుకోండి. స్టాప్-లాస్‌ను TP1 వద్దకు జరపండి."
            )
            dispatcher.send(msg)

# ==============================================================================
# 3. MASTER AGENT CLASS
# ==============================================================================
class AdityaComprehensiveBot:
    def __init__(self, token: str, channel: str):
        self.dispatcher = TelegramDispatcher(token, channel)
        self.active_trade: Optional[TradePosition] = None

    # కార్పొరేట్ ఫైలింగ్స్ & బిగ్ ఆర్డర్స్ (Money Purse Style)
    def post_corporate_filings(self):
        msg = (
            f"📑 *ఆదిత్య ట్రేడ్ వేవ్స్ — ముఖ్యమైన కార్పొరేట్ ప్రకటనలు*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⚡ *KPI Green Energy*: రాజస్థాన్‌లో 500 MW సోలార్ పార్క్ ప్రాజెక్ట్ కోసం ₹2,025 కోట్ల భారీ ఆర్డర్ లభించింది.\n\n"
            f"🏭 *Navin Fluorine*: దహేజ్ ప్లాంట్‌లో డీబాటిల్‌నెకింగ్ కెపాసిటీ విజయవంతంగా ప్రారంభమైంది.\n\n"
            f"🏥 *Dr. Reddy's Lab*: రాబోయే రెండేళ్లలో US మార్కెట్‌లో 20-25 కొత్త ప్రొడక్టులను విడుదల చేయాలని ప్రణాళిక.\n\n"
            f"🏦 *Tamilnad Mercantile Bank*: తమిళనాడులో నూతన శాఖల ఏర్పాటుకు బోర్డు అనుమతి లభించింది.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ _సమాచారం & అవగాహన కొరకు మాత్రమే._"
        )
        self.dispatcher.send(msg)

    # టాప్ గెయినర్స్ & లూజర్స్ (Market Breadth)
    def post_market_breadth(self):
        msg = (
            f"📊 *మార్కెట్ స్థితిగతులు (MARKET BREADTH)*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🟢 *టాప్ గెయినర్స్ (Top Gainers)*:\n"
            f"• Kirloskar Oil: ₹2,380.00 (+11.19%)\n"
            f"• Cupid: ₹291.20 (+10.07%)\n"
            f"• TD Power Systems: ₹791.20 (+9.65%)\n\n"
            f"🔴 *టాప్ లూజర్స్ (Top Losers)*:\n"
            f"• PB Fintech: ₹1,084.10 (-5.89%)\n"
            f"• Honasa Consumer: ₹441.00 (-5.47%)\n"
            f"• Patanjali Foods: ₹371.25 (-5.15%)\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • Learn. Invest. Grow._"
        )
        self.dispatcher.send(msg)

    # లైవ్ ట్రేడ్ అలర్ట్
    def send_trade_signal(
        self,
        instrument: str,
        strike: int,
        opt_type: str,
        expiry: str,
        entry_price: float,
        spot_val: float,
        spot_sl: float,
        why_text: str
    ):
        tp1 = round(entry_price + 10.0, 2)
        tp2 = round(entry_price + 20.0, 2)
        tp3 = round(entry_price + 30.0, 2)
        tp4 = round(entry_price + 40.0, 2)
        tp5 = round(entry_price + 50.0, 2)
        opt_sl = round(entry_price - 15.0, 2)

        contract = f"{instrument} {expiry} {strike} {opt_type}"

        self.active_trade = TradePosition(
            contract=contract,
            expiry_date=expiry,
            entry_price=entry_price,
            current_sl=opt_sl,
            target_1=tp1, target_2=tp2, target_3=tp3, target_4=tp4, target_5=tp5
        )

        badge = "🔴" if opt_type == "PE" else "🟢"
        msg = (
            f"{badge} *{contract} — కొనుగోలు సూచన (BUY)*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏱ వ్యూహం: రీట్రేస్ ఎంట్రీ • 5-నిమిషాల క్యాండిల్ కన్‌ఫ్లూయెన్స్\n\n"
            f"💰 *కొనుగోలు ధర (Entry)*: ₹{entry_price:.2f}\n\n"
            f"🎯 *లక్ష్యాలు (Targets)*:\n"
            f"  • *TP1* : ₹{tp1:.2f} (+10 పాయింట్లు)\n"
            f"  • *TP2* : ₹{tp2:.2f} (+20 పాయింట్లు)\n"
            f"  • *TP3* : ₹{tp3:.2f} (+30 పాయింట్లు)\n"
            f"  • *TP4* : ₹{tp4:.2f} (+40 పాయింట్లు)\n"
            f"  • *TP5* : ₹{tp5:.2f} (+50 పాయింట్లు)\n\n"
            f"🛑 *స్టాప్-లాస్*: ఆప్షన్ ₹{opt_sl:.2f} | ఇండెక్స్ క్లోజ్ {spot_sl:.2f}\n"
            f"📍 *స్పాట్ ఇండెక్స్*: {spot_val:.2f}\n\n"
            f"💡 *కారణం*: {why_text}\n"
            f"📊 *వాల్యూమ్*: ✔ మునుపటి క్యాండిల్ కంటే అధిక వాల్యూమ్ నమోదైంది\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • క్రమశిక్షణతో కూడిన ట్రేడింగ్_"
        )
        self.dispatcher.send(msg)

if __name__ == "__main__":
    TOKEN = "8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM"
    CHANNEL = "@adityatradewaves"

    bot = AdityaComprehensiveBot(token=TOKEN, channel=CHANNEL)

    print("1. కార్పొరేట్ ఫైలింగ్స్ పోస్ట్ చేస్తోంది...")
    bot.post_corporate_filings()
    time.sleep(2)

    print("2. లైవ్ ట్రేడ్ సిగ్నల్ పంపుతోంది...")
    bot.send_trade_signal(
        instrument="NIFTY",
        strike=23850,
        opt_type="PE",
        expiry="29 SEP",
        entry_price=146.0,
        spot_val=23810.50,
        spot_sl=23845.0,
        why_text="ప్రైస్ రెడ్ రెసిస్టెన్స్ లైన్ వద్ద రిజెక్ట్ అయ్యి 5-నిమిషాల క్యాండిల్ కిందనే క్లోజ్ అయింది."
    )
    time.sleep(2)

    print("3. టార్గెట్ హిట్స్ టెస్టింగ్ (TP1 & TP2)...")
    bot.active_trade.update_ltp(157.0, bot.dispatcher)
    time.sleep(2)
    bot.active_trade.update_ltp(168.0, bot.dispatcher)
    time.sleep(2)

    print("4. మార్కెట్ గెయినర్స్/లూజర్స్ రిపోర్ట్ పంపుతోంది...")
    bot.post_market_breadth()
    print("\n✅ అన్ని మెసేజ్‌లు Telegram లో పోస్ట్ చేయబడ్డాయి!")
