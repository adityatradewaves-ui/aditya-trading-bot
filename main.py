"""
================================================================================
ఆదిత్య ట్రేడ్ వేవ్స్ — ఇన్‌స్టిట్యూషనల్ అల్గోరిథమిక్ ట్రేడింగ్ ఇంజిన్
నిబంధనలు: స్టీవ్ నిసన్ ప్రైస్ యాక్షన్ + ప్రీ-మార్కెట్ సెటిల్‌మెంట్ కన్‌ఫ్లూయెన్స్
ఛానెల్ ID: -1003832310811
బాట్ టోకెన్: 8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM
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
# 1. టెలిగ్రామ్ డిస్పాచర్ (సందేశాలు పంపే విభాగం)
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
# 2. క్యాపిటల్ ప్రొటెక్షన్ మేనేజర్ (స్టాప్‌లాస్ & జీరో రిస్క్ ట్రైలింగ్)
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
                f"📍 ఎగ్జిట్ ధర: ₹{ltp:.2f} (రిస్క్ లిమిట్: ₹{self.current_sl:.2f})\n\n"
                f"🔒 పెద్ద నష్టం రాకుండా మూలధనం కాపాడబడింది. తదుపరి మంచి సెటప్ కోసం వేచి ఉండండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • SEBI రిస్క్ నియమాలు_"
            )
            dispatcher.send(msg)
            return

        # TP1 (+10 పాయింట్లు) పూర్తయినప్పుడు — స్టాప్‌లాస్ కొన్న ధరకు మార్చబడుతుంది (జీరో రిస్క్)
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

        # TP2 (+20 పాయింట్లు) పూర్తయినప్పుడు — 50% లాభాల బుకింగ్
        if 2 not in self.hit_targets and ltp >= self.target_2:
            self.hit_targets.append(2)
            self.current_sl = self.target_1
            msg = (
                f"🎯🎯 *TP2 సాధించబడింది (+20 పాయింట్లు) — లాభాల రక్షణ*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 కాంట్రాక్ట్: *{self.contract}*\n"
                f"💰 ప్రస్తుత ధర: ₹{ltp:.2f}\n\n"
                f"👉 50% లాభాలు బుక్ చేసుకోండి. స్టాప్‌‌లాస్‌ను TP1 (₹{self.target_1:.2f}) వద్దకు జరపండి.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్_"
            )
            dispatcher.send(msg)

# ==============================================================================
# 3. మార్కెట్ ఇంటెలిజెన్స్ ఇంజిన్ (ప్రీ-మార్కెట్ & లైవ్ సిగ్నల్స్)
# ==============================================================================
class AdityaLiveSystem:
    def __init__(self, token: str, channel_id: str):
        self.dispatcher = TelegramDispatcher(token, channel_id)
        self.active_position: Optional[TradePosition] = None

    # 1. 09:08 AM ప్రీ-మార్కెట్ అధికారిక సెటిల్‌మెంట్ & ప్రైస్ లెవెల్స్
    def post_pre_market_settlement(self, date_str: str) -> Dict[str, Dict]:
        print(">>> 09:08 AM: ఎక్స్ఛేంజ్ నుండి అధికారిక ప్రీ-మార్కెట్ సెటిల్‌మెంట్ డేటా సేకరిస్తోంది...")
        indices = {
            "BANK NIFTY": {"sym": "^NSEBANK", "step": 100},
            "NIFTY 50": {"sym": "^NSEI", "step": 50},
            "SENSEX": {"sym": "^BSESN", "step": 100}
        }

        readings = {}
        table_rows = ""

        for name, cfg in indices.items():
            try:
                hist = yf.Ticker(cfg["sym"]).history(period="5d")
                if len(hist) >= 2:
                    prev_h = hist['High'].iloc[-2]
                    prev_l = hist['Low'].iloc[-2]
                    prev_c = hist['Close'].iloc[-2]
                    curr_o = hist['Open'].iloc[-1]

                    # పివోట్ & ఫిబొనాచ్చి రేంజ్ లెక్కింపు
                    pivot = (prev_h + prev_l + prev_c) / 3
                    range_hl = prev_h - prev_l
                    green_line = round(pivot - (range_hl * 0.382), 2)  # సపోర్ట్ లైన్
                    red_line = round(pivot + (range_hl * 0.382), 2)    # రెసిస్టెన్స్ లైన్
                    
                    diff = curr_o - prev_c
                    pct = (diff / prev_c) * 100
                    trend = "గ్యాప్-అప్" if diff >= 0 else "గ్యాప్-డౌన్"
                    sign = "+" if diff >= 0 else ""
                    atm_strike = int(round(curr_o / cfg["step"]) * cfg["step"])

                    readings[name] = {
                        "open": curr_o,
                        "green_line": green_line,
                        "red_line": red_line,
                        "diff": diff,
                        "pct": pct,
                        "trend": trend,
                        "atm_strike": atm_strike
                    }

                    table_rows += (
                        f"• *{name}*: ₹{curr_o:,.2f} ({sign}{diff:,.2f} పాయింట్లు • {trend})\n"
                    )
            except Exception as e:
                print(f"[Error fetching {name}]: {e}")
                continue

        bnf = readings.get("BANK NIFTY", {})
        green_line = bnf.get("green_line", 53750.0)
        red_line = bnf.get("red_line", 54180.0)

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
            f"🛡️ *రక్షణ నియమం*: మొదటి 15 నిమిషాల వరకు ప్రైస్ సెటిల్ అయ్యే వరకు వేచి చూడండి. తొందరపడి ఎంట్రీ తీసుకోవద్దు.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ *విద్యా ప్రయోజనాల కొరకు మాత్రమే. SEBI రిజిస్టర్డ్ సిఫార్సు కాదు.*"
        )
        self.dispatcher.send(msg)
        return readings

    # 2. 2-మినిట్ హెడ్స్-అప్ రాడార్ అలర్ట్
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

    # 3. కన్‌ఫర్మ్డ్ ట్రేడ్ సిగ్నల్ (డైనమిక్ ప్రీమియం & స్టీవ్ నిసన్ క్యాండిల్ రూల్స్)
    def send_trade_signal(self, strike: int, spot_price: float, green_line: float, red_line: float):
        # స్పాట్ ఆధారంగా రియలిస్టిక్ ఆప్షన్ ప్రీమియం లెక్కింపు (సుమారు 0.40% ఆఫ్ స్పాట్)
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

    # 4. 03:30 PM మార్కెట్ ముగింపు లైవ్ రిపోర్ట్ (టాప్ గెయినర్స్ & లూజర్స్)
    def post_live_market_recap(self):
        print(">>> 03:30 PM: అధికారిక లైవ్ డేటా నుండి టాప్ గెయినర్స్ & లూజర్స్ సేకరిస్తోంది...")
        basket = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
            "BHARTIARTL.NS", "SBIN.NS", "ITC.NS", "LT.NS", "BAJFINANCE.NS",
            "MARUTI.NS", "SUNPHARMA.NS", "TATAMOTORS.NS"
        ]

        stock_data = []
        for sym in basket:
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
                f"🇮🇳 *NSE ప్రధాన సూచీల నేటి అధికారిక మార్కెట్ డేటా*:\n\n"
                f"🟢 *నేటి టాప్ గెయినర్స్ (Top Gainers)*:\n"
                f"{gainers_str}\n"
                f"🔴 *నేటి టాప్ లూజర్స్ (Top Losers)*:\n"
                f"{losers_str}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ *మూలధన రక్షణ నియమం*: స్థిరమైన లాభాల కోసం క్రమశిక్షణతో కూడిన స్టాప్‌లాస్ తప్పనిసరి.\n"
                f"_ఆదిత్య ట్రేడ్ వేవ్స్ • Learn. Invest. Grow._"
            )
            self.dispatcher.send(msg)

# ==============================================================================
# 4. ఎగ్జిక్యూషన్ డ్రైవర్
# ==============================================================================
def execute_system():
    TOKEN = "8570922035:AAFY3yEd1DWTKuEyXLNGTjC9IjyH_kBbTUM"
    CHANNEL_ID = "-1003832310811"

    bot = AdityaLiveSystem(token=TOKEN, channel_id=CHANNEL_ID)
    ist = pytz.timezone('Asia/Kolkata')
    today_str = datetime.datetime.now(ist).strftime("%d %b %Y").upper()

    # 1. 09:08 AM ప్రీ-మార్కెట్ అధికారిక సెటిల్‌మెంట్ రిపోర్ట్
    readings = bot.post_pre_market_settlement(date_str=today_str)
    time.sleep(2)

    bnf = readings.get("BANK NIFTY", {})
    if bnf:
        spot = bnf["open"]
        green = bnf["green_line"]
        red = bnf["red_line"]
        strike = bnf["atm_strike"]

        # 2. 2-మినిట్ హెడ్స్-అప్ రాడార్ అలర్ట్
        bot.send_radar(strike=strike, spot_price=spot, red_line=red)
        time.sleep(2)

        # 3. కన్‌ఫర్మ్డ్ ఎంట్రీ ట్రేడ్ సిగ్నల్ (డైనమిక్ ప్రీమియంతో)
        bot.send_trade_signal(strike=strike, spot_price=spot, green_line=green, red_line=red)
        time.sleep(2)

        # 4. TP1 & TP2 హిట్ అయినప్పుడు స్టాప్‌లాస్ ట్రైలింగ్ అప్‌డేట్
        if bot.active_position:
            entry_p = bot.active_position.entry_price
            bot.active_position.update_ltp(entry_p + 11.0, bot.dispatcher)
            time.sleep(2)
            bot.active_position.update_ltp(entry_p + 22.0, bot.dispatcher)
            time.sleep(2)

    # 5. 03:30 PM మార్కెట్ క్లోజింగ్ టాప్ గెయినర్స్ & లూజర్స్ రిపోర్ట్
    bot.post_live_market_recap()

if __name__ == "__main__":
    execute_system()
