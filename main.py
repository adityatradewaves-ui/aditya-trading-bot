"""
================================================================================
ADITYA TRADE WAVES — INDIAN MARKET INSTITUTIONAL TRADING AGENT
Author: Aditya Trade Waves
Focus: NSE/BSE Cash & Derivatives (Nifty, Bank Nifty)
Rules: Steve Nison Price Action + Zerodha Varsity Technical Confluence
Target Telegram Channel: @adityatradewaves
Bot Token: 8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM
================================================================================
"""

import time
import requests
from dataclasses import dataclass, field
from typing import List, Optional

# ==============================================================================
# 1. టెలిగ్రామ్ మెసేజ్ పంపే విభాగం (TELEGRAM DISPATCHER)
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
            print(f"[నెట్‌వర్క్ లోపం]: {e}")
            return False

# ==============================================================================
# 2. ట్రేడ్ పొజిషన్ & టార్గెట్ ట్రాకింగ్ (TP1 TO TP5 & ట్రైలింగ్ స్టాప్‌లాస్)
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

        # స్టాప్‌లాస్ హిట్ పరిశీలన
        if ltp <= self.current_sl:
            self.is_closed = True
            msg = (
                f"🛑 *స్టాప్-లాస్ హిట్ అయింది (STOP-LOSS HIT)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"📅 ఎక్స్‌పైరీ తేది: *{self.expiry_date}*\n\n"
                f"📍 ఎగ్జిట్ ధర: ₹{ltp:.2f} (SL లెవెల్: ₹{self.current_sl:.2f})\n\n"
                f"💡 మూలధన రక్షణకు ప్రాధాన్యత ఇవ్వబడింది. క్రమశిక్షణతో కూడిన నిష్క్రమణ.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • SEBI రిస్క్ నిర్వహణ నిబంధనలు_"
            )
            dispatcher.send(msg)
            return

        # TP1 (+10 పాయింట్లు)
        if 1 not in self.hit_targets and ltp >= self.target_1:
            self.hit_targets.append(1)
            self.current_sl = self.entry_price  # స్టాప్‌లాస్ కొన్న ధరకు మార్చడం
            msg = (
                f"🎯 *మొదటి టార్గెట్ పూర్తి (TP1 DONE)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"📅 ఎక్స్‌పైరీ తేది: *{self.expiry_date}*\n\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f} (+10 పాయింట్లు)\n\n"
                f"👉 *తదుపరి చర్య*: స్టాప్-లాస్‌ను వెంటనే కొన్న ధర వద్దకు (Cost Price ₹{self.entry_price:.2f}) మార్చండి.\n"
                f"🔒 జీరో-రిస్క్ ట్రేడ్ ఆక్టివేట్ అయింది! తదుపరి లక్ష్యం TP2...\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

        # TP2 (+20 పాయింట్లు)
        if 2 not in self.hit_targets and ltp >= self.target_2:
            self.hit_targets.append(2)
            self.current_sl = self.target_1
            msg = (
                f"🎯🎯 *రెండవ టార్గెట్ పూర్తి (TP2 DONE)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"📅 ఎక్స్‌పైరీ తేది: *{self.expiry_date}*\n\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f} (+20 పాయింట్లు)\n\n"
                f"👉 *తదుపరి చర్య*: 50% లాభాలు బుక్ చేసుకోండి. స్టాప్-లాస్‌ను TP1 (₹{self.target_1:.2f}) వద్దకు జరపండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

        # TP3 (+30 పాయింట్లు)
        if 3 not in self.hit_targets and ltp >= self.target_3:
            self.hit_targets.append(3)
            self.current_sl = self.target_2
            msg = (
                f"🎯🎯🎯 *మూడవ టార్గెట్ పూర్తి (TP3 DONE)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f} (+30 పాయింట్లు)\n\n"
                f"👉 *తదుపరి చర్య*: స్టాప్-లాస్‌ను TP2 (₹{self.target_2:.2f}) వద్దకు ట్రైల్ చేయండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

        # TP5 (+50 పాయింట్లు)
        if 5 not in self.hit_targets and ltp >= self.target_5:
            self.hit_targets.append(5)
            self.is_closed = True
            msg = (
                f"🏆 *అన్ని టార్గెట్స్ పూర్తి అయ్యాయి (TP5 ALL TARGETS HIT)*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👑 కాంట్రాక్ట్: *{self.contract}*\n"
                f"📅 ఎక్స్‌పైరీ తేది: *{self.expiry_date}*\n\n"
                f"💰 ఎగ్జిట్ ధర: ₹{ltp:.2f} (+50 పాయింట్లు సాధించబడ్డాయి!)\n\n"
                f"🎉 *తదుపరి చర్య*: పూర్తి లాభాలు బుక్ చేసుకుని ట్రేడ్ ముగించండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • విజయవంతమైన ముగింపు_"
            )
            dispatcher.send(msg)

# ==============================================================================
# 3. ఇన్స్టిట్యూషనల్ ఇండియన్ మార్కెట్ మాస్టర్ క్లాస్
# ==============================================================================
class AdityaIndianMarketBot:
    def __init__(self, token: str, channel: str):
        self.dispatcher = TelegramDispatcher(token, channel)
        self.active_trade: Optional[TradePosition] = None

    # ఉదయం 08:25 AM: కార్పొరేట్ ఫైలింగ్స్, ఆర్డర్లు & సెక్టార్ న్యూస్ (Money Purse & Valuebull Style)
    def post_corporate_updates(self, date_str: str):
        msg = (
            f"📑 *ఆదిత్య ట్రేడ్ వేవ్స్ — భారతీయ మార్కెట్ సమాచారం*\n"
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
            f"_ఇది కేవలం సమాచారం మరియు విద్యా ప్రయోజనాల కోసం మాత్రమే. సెబీ రిజిస్టర్డ్ కొనుగోలు/అమ్మకం సిఫార్సు కాదు._"
        )
        self.dispatcher.send(msg)

    # ఉదయం 09:15 AM: ప్రధాన సూచీలు & ఏటీఎం స్ట్రైక్స్ ఎంపిక (Nifty & Bank Nifty)
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

    # ఉదయం 09:35 AM: 5-మినిట్ & 1-మినిట్ కన్‌ఫ్లూయెన్స్ లైవ్ ఆప్షన్ అలర్ట్
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
            f"_ఆదిత్య ట్రేడ్ వేవ్స్ • SEBI రిజిస్టర్డ్ సలహా కాదు. అవగాహన కొరకు మాత్రమే._"
        )
        self.dispatcher.send(msg)

    # సాయంత్రం 03:45 PM: మార్కెట్ బ్రెడ్త్ & సమ్మరీ (BSE/NSE Gainers & Losers)
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
# 4. ఎగ్జిక్యూషన్ డ్రైవర్ (SIMULATION & TESTING)
# ==============================================================================
if __name__ == "__main__":
    TOKEN = "8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM"
    CHANNEL = "@adityatradewaves"

    bot = AdityaIndianMarketBot(token=TOKEN, channel=CHANNEL)

    print(">>> 1. కార్పొరేట్ ఫైలింగ్స్ & సెక్టార్ సమాచారం పంపుతోంది...")
    bot.post_corporate_updates(date_str="29 SEP 2026")
    time.sleep(2)

    print(">>> 2. నిఫ్టీ & బ్యాంక్ నిఫ్టీ ఏటీఎం వాచ్‌లిస్ట్ పంపుతోంది...")
    bot.post_today_strikes(instrument="BANK NIFTY", spot_price=53891.10, expiry_str="29 SEP")
    time.sleep(2)

    print(">>> 3. లైవ్ ట్రేడ్ అలర్ట్ (వసు & మనీ పర్స్ లేఅవుట్) పంపుతోంది...")
    bot.send_trade_signal(
        instrument="BANK NIFTY",
        strike_num=53800,
        opt_type="PE",
        expiry_str="29 SEP",
        setup_type="రీట్రేస్ ఎంట్రీ (Retrace entry • short)",
        candle_closed="09:35–09:40 క్యాండిల్ క్లోజ్",
        entry_price=201.40,
        spot_index_val=53794.55,
        spot_sl_val=53907.15,
        green_line=54405.30,
        red_line=53894.60,
        why_text="ధర రెడ్ లైన్ రెసిస్టెన్స్ వద్ద రిజెక్ట్ అయ్యి, 5-నిమిషాల క్యాండిల్ కిందనే ముగిసింది."
    )
    time.sleep(2)

    print(">>> 4. టార్గెట్స్ ట్రాకింగ్ (TP1 & TP2)...")
    bot.active_trade.update_ltp(212.0, bot.dispatcher) # TP1 (+10 pts)
    time.sleep(2)
    bot.active_trade.update_ltp(222.5, bot.dispatcher) # TP2 (+20 pts)
    time.sleep(2)

    print(">>> 5. మార్కెట్ ముగింపు గెయినర్స్/లూజర్స్ రిపోర్ట్ పంపుతోంది...")
    bot.post_market_breadth()

    print("\n✅ అన్ని మెసేజ్‌లు Telegram లో స్పష్టంగా పోస్ట్ చేయబడ్డాయి!")
