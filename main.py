# =========================================================
# INSTALL:
# pip install python-telegram-bot==13.15
# =========================================================

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)

from telegram.error import BadRequest

import random
import threading
import time
import json
import os

# =========================================================
# CONFIG
# =========================================================

TOKEN = "8952356657:AAFGucvpND34zJa5CIgs05GAuYGboxz0nKs"

OWNER_ID = 6531314640
EXTRA_ADMIN = 8650959684

DATA_FILE = "bot_data.json"

# =========================================================
# SAVE SYSTEM
# =========================================================

leaderboard = {}

events = {
    "giveaway": None,
    "premium": None
}

quiz_data = {}

# =========================================================
# SAVE / LOAD
# =========================================================

def save_data():

    data = {
        "leaderboard": leaderboard,
        "events": events,
        "quiz_data": quiz_data,
        "tournament_players": tournament_players,
        "tournament_winners": tournament_winners
    }

    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


def load_data():

    global leaderboard, events, quiz_data
    global tournament_players, tournament_winners

    if not os.path.exists(DATA_FILE):
        return

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except:
        return

    leaderboard = {
        int(k): v
        for k, v in data.get("leaderboard", {}).items()
    }

    quiz_data = data.get("quiz_data", {}) or {}

    tournament_players = data.get("tournament_players", []) or []
    tournament_winners = data.get("tournament_winners", []) or []

    events = data.get("events", {
        "giveaway": None,
        "premium": None
    })


load_data()

# =========================================================
# TAP RACE GLOBALS
# =========================================================

taprace_match = []

taprace_taps = {}

taprace_active = False
taprace_started = False
taprace_message_id = None

last_tap = {}

match_running = False

tournament_players = []

tournament_winners = []

# =========================================================
# QUESTIONS
# =========================================================

car_q = [

("Which engine powers MK4 Supra?", "2jz"),
("Which car is called Godzilla?", "nissan gtr"),
("Which brand makes RX7?", "mazda"),
("Who owns Lamborghini?", "volkswagen"),
("Engine of Skyline R34?", "rb26"),
("Who made NSX?", "honda"),
("Car with B58 engine?", "bmw"),
("WRX drivetrain?", "awd"),
("Prancing horse logo?", "ferrari"),
("Hellcat brand?", "dodge"),

("Who makes 350z?", "nissan"),
("Civic Type R brand?", "honda"),
("Fastest Bugatti?", "chiron"),
("Meaning of GTR?", "gran turismo racer"),
("Lancer Evolution brand?", "mitsubishi"),
("Supra brand?", "toyota"),
("Mustang brand?", "ford"),
("Audi R8 brand?", "audi"),
("Porsche 911 brand?", "porsche"),
("Jesko brand?", "koenigsegg"),

("Huayra brand?", "pagani"),
("Model S brand?", "tesla"),
("P1 brand?", "mclaren"),
("Corvette brand?", "chevrolet"),
("GT86 brand?", "toyota"),
("Aventador brand?", "lamborghini"),
("Rotary engine car?", "mazda rx7"),
("BMW performance division?", "m"),
("Dodge Demon engine type?", "v8"),
("Senna brand?", "mclaren"),

("Which engine powers Lexus LFA?", "1lr-gue"),
("What turbo setup does RB26 use?", "twin turbo"),
("What drivetrain is Audi Quattro?", "awd"),
("Transmission of MK4 Supra RZ?", "getrag v160"),
("Which brand made F40?", "ferrari"),
("What engine powers Nissan Silvia S15?", "sr20det"),
("Who makes Chiron?", "bugatti"),
("Which company owns Bentley?", "volkswagen"),
("What engine powers Dodge Hellcat?", "supercharged v8"),
("Which company makes AMG?", "mercedes")

]

# =========================================================

math_q = [

("125 x 24", "3000"),
("15²", "225"),
("√196", "14"),
("45 x 11", "495"),
("18³", "5832"),
("900 ÷ 30", "30"),
("77 + 88", "165"),
("1000 - 457", "543"),
("13 x 13", "169"),
("99 x 9", "891"),

("144 x 2", "288"),
("256 ÷ 16", "16"),
("121 ÷ 11", "11"),
("17 x 17", "289"),
("400 ÷ 25", "16"),
("36 x 12", "432"),
("625 ÷ 25", "25"),
("150 - 73", "77"),
("81 ÷ 9 + 10", "19"),
("64 ÷ 8 + 9", "17"),

("250 ÷ 5 x 3", "150"),
("72 ÷ 9 x 6", "48"),
("(50 x 2) - 35", "65"),
("144 ÷ 12 + 7", "19"),
("999 ÷ 3", "333"),
("45²", "2025"),
("√625", "25"),
("88 x 12", "1056"),
("500 - 275", "225"),
("(125 × 12) + (50 ÷ 2)", "1525"),

("√2025", "45"),
("(18² + 24²)", "900"),
("(99 × 99)", "9801"),
("(144 ÷ 12) × (17 - 5)", "144"),
("(81 x 9) - 100", "629"),
("(500 ÷ 5) + 777", "877"),
("(15 x 15) + (25 x 4)", "325"),
("(64 ÷ 8)²", "64"),
("(90 x 11)", "990"),
("50 x 50", "2500")

]

# =========================================================

puzzle_q = [

("R O F D", "ford"),
("I D U A", "audi"),
("A D Z M A", "mazda"),
("A Y T O O T", "toyota"),
("S U X E L", "lexus"),
("W M B", "bmw"),
("A D G O D", "dodge"),
("A R F R E R I", "ferrari"),
("A G A P N I", "pagani"),
("T T I U A B G", "bugatti"),

("R O P E H S C", "porsche"),
("U S B R A U", "subaru"),
("M A C N E R L", "mclaren"),
("K G G O I E N S E", "koenigsegg"),
("A T E S L", "tesla"),
("A N H O D", "honda"),
("A N S I N S", "nissan"),
("Y E V O T H C E R L", "chevrolet"),
("A I K S Y L N E", "skyline"),
("A U S R P", "supra"),

("O N C H R I", "chiron"),
("A N E S N", "senna"),
("A J O K S E", "jesko"),
("A R Y A U H", "huayra"),
("A R G T", "gtr"),
("R B ✌ 6", "rb26"),
("✌ j Z", "2jz"),
("A R X 7", "rx7"),
("🌲 5 0 Z", "350z"),
("✈️ R A R I F E R", "ferrari"),

("🦇 M B W", "bmw"),
("💀 A N I G A P", "pagani"),
("⚡ S A L E T", "tesla"),
("🔥 T G R", "gtr"),
("👑 R A Y H U A", "huayra"),
("🏁 N A N S I S", "nissan"),
("🚗 O Y O T T A", "toyota"),
("💨 R U S B A U", "subaru"),
("🛞 D O F R", "ford"),
("⚔️ H E C O R S P", "porsche")

]

# =========================================================

logo_q = [

("4 rings logo?", "audi"),
("Horse logo?", "ferrari"),
("Bull logo?", "lamborghini"),
("Electric Elon brand?", "tesla"),
("Stars Japan brand?", "subaru"),
("BMW round logo?", "bmw"),
("Trident logo?", "maserati"),
("Wings logo?", "bentley"),
("Snake logo?", "dodge"),
("Shield logo?", "porsche"),

("Rotary engine brand?", "mazda"),
("3 diamonds logo?", "mitsubishi"),
("Korean modern logo?", "hyundai"),
("Lightning logo?", "opel"),
("Swedish luxury brand?", "volvo"),
("Oval Japan logo?", "toyota"),
("Horse muscle brand?", "ford"),
("Lion logo?", "peugeot"),
("Nissan luxury division?", "infiniti"),
("Honda luxury division?", "acura"),

("Diamond French brand?", "renault"),
("Hypercar Pagani brand?", "pagani"),
("Koenigsegg brand?", "koenigsegg"),
("Chiron brand?", "bugatti"),
("Senna brand?", "mclaren"),
("Supra maker?", "toyota"),
("Skyline maker?", "nissan"),
("NSX maker?", "honda"),
("LFA maker?", "lexus"),
("RX7 maker?", "mazda"),

("What brand uses griffin logo?", "saab"),
("Luxury division of Toyota?", "lexus"),
("Luxury division of Hyundai?", "genesis"),
("What brand has scorpion logo?", "abarth"),
("What logo has double chevron?", "citroen"),
("Italian supercar bull logo?", "lamborghini"),
("Which logo has blue oval?", "ford"),
("Which company owns Mini?", "bmw"),
("Which logo has star emblem?", "mercedes"),
("What logo has ram head?", "dodge")

]

# =========================================================
# HELPERS
# =========================================================

def now():

    return int(time.time())


def is_admin(update):

    uid = update.effective_user.id

    return uid in [
        OWNER_ID,
        EXTRA_ADMIN
    ]


def safe_name(user):

    if user.username:

        return f"@{user.username}"

    return user.first_name


def format_time(sec):

    days = sec // 86400
    sec %= 86400

    hours = sec // 3600
    sec %= 3600

    mins = sec // 60
    sec %= 60

    if days > 0:
        return f"{days}d {hours}h {mins}m"

    if hours > 0:
        return f"{hours}h {mins}m {sec}s"

    return f"{mins:02d}:{sec:02d}"

# =========================================================
# START
# =========================================================

def start(update, context):

    update.message.reply_text(
"""
━━━━━━━━━━━━━━━━━━
🏁 TNNR GIVEAWAY BOT
━━━━━━━━━━━━━━━━━━
🔥 BOT ONLINE 🔥
━━━━━━━━━━━━━━━━━━
MAKER : MARK MWEHEHEHE
━━━━━━━━━━━━━━━━━━
🎮 GAMES 😎😎😎😎😎😎
━━━━━━━━━━━━━━━━━━
🚗 CAR QUIZ
🧠 MATH QUIZ
🧩 PUZZLE GAME
🚘 CAR LOGO QUIZ
🏁 TAP RACE TOURNAMENT
━━━━━━━━━━━━━━━━━━
🎁 GIVEAWAY🎁
👑 PREMIUM GIVEAWAY👑
━━━━━━━━━━━━━━━━━━
"""
    )

# =========================================================
# PROFILE
# =========================================================

def profile(update, context):

    user = update.message.from_user

    wins = leaderboard.get(
        user.id,
        0
    )

    update.message.reply_text(
f"""
━━━━━━━━━━━━━━━━━━
👤 PLAYER PROFILE👤
━━━━━━━━━━━━━━━━━━
👤 USER: {safe_name(user)}👤
━━━━━━━━━━━━━━━━━━
🏆 WINS: {wins}👑
━━━━━━━━━━━━━━━━━━
🏹NICE ONE BRO BRO🏹
━━━━━━━━━━━━━━━━━━
"""
    )

# =========================================================
# LEADERBOARD
# =========================================================

def leaderboard_cmd(update, context):

    text = (
"""
━━━━━━━━━━━━━━━━━━
🏆 LEADERBOARD 👑
━━━━━━━━━━━━━━━━━━
🫡WOW YOU CAME TO THAT?
━━━━━━━━━━━━━━━━━━
 OHHH NAHH 🫡
━━━━━━━━━━━━━━━━━━
"""
    )

    sorted_players = sorted(
        leaderboard.items(),
        key=lambda x: x[1],
        reverse=True
    )

    if not sorted_players:

        text += "\n❌ NO PLAYERS"

    for i, (uid, wins) in enumerate(
        sorted_players[:10],
        start=1
    ):

        try:

            user = context.bot.get_chat(uid)

            text += (
                f"\n{i}. "
                f"{safe_name(user)}"
                f" - {wins}"
            )

        except:
            pass

    update.message.reply_text(text)
    
    # =========================================================
# TIMER LOOP
# =========================================================

def timer_loop(bot):

    while True:

        try:

            for key in ["giveaway", "premium"]:

                ev = events.get(key)

                if not ev:
                    continue

                # SAFETY CHECK (important after restart)
                if "end" not in ev or "chat_id" not in ev or "message_id" not in ev:
                    continue

                remaining = ev["end"] - now()

                if remaining <= 0:

                    finish_event(bot, key)

                else:

                    try:
                        update_event(bot, key, remaining)
                    except Exception as e:
                        print(f"[UPDATE EVENT ERROR {key}]:", e)

        except Exception as e:
            print("[TIMER LOOP ERROR]:", e)

        time.sleep(1)
# =========================================================
# UPDATE EVENT
# =========================================================

def update_event(bot, key, remaining):

    ev = events.get(key)
    if not ev:
        return

    try:

        total = len(ev.get("players", []))

        start_date = time.strftime(
            "%Y-%m-%d %I:%M %p",
            time.localtime(ev["start"])
        )

        end_date = time.strftime(
            "%Y-%m-%d %I:%M %p",
            time.localtime(ev["end"])
        )

        bar = "🟩" * int((remaining / ev["duration"]) * 10)
        bar += "⬜" * (10 - len(bar))

        if key == "giveaway":
            button_text = f"🎁 JOIN GIVEAWAY ({total})"
            callback = "join_giveaway"
        else:
            button_text = f"👑 JOIN PREMIUM ({total})"
            callback = "join_premium"

        keyboard = [[
            InlineKeyboardButton(button_text, callback_data=callback)
        ]]

        bot.edit_message_text(
            chat_id=ev["chat_id"],
            message_id=ev["message_id"],

            text=f"""
━━━━━━━━━━━━━━━━━━
{ev['title']}
━━━━━━━━━━━━━━━━━━
🔥 LIVE EVENT 🔥
━━━━━━━━━━━━━━━━━━
━━━━━━━━━━━━━━━━━━
🎁 PRIZE:
{ev['prize']}
━━━━━━━━━━━━━━━━━━
👥 PLAYERS: {total}
🏆 ONLY ONE WINNER
━━━━━━━━━━━━━━━━━━
⚡ JOIN NOW AND WIN ⚡
━━━━━━━━━━━━━━━━━━
⏳ TIME LEFT:
{format_time(remaining)}
━━━━━━━━━━━━━━━━━━
{bar}
━━━━━━━━━━━━━━━━━━
📅 STARTED:
{start_date}
━━━━━━━━━━━━━━━━━━
🏁 ENDS:
{end_date}
━━━━━━━━━━━━━━━━━━
IF YOU CAN'T PARTICIPATE IN
 THE GIVEAWAY, THE BOT IS OFF...
━━━━━━━━━━━━━━━━━━
""",

            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except:
        return

# =========================================================
# FINISH EVENT
# =========================================================

def finish_event(
    bot,
    key
):

    ev = events[key]

    if not ev:
        return

    if ev["players"]:

        winner = random.choice(
            ev["players"]
        )

        user = bot.get_chat(
            winner
        )

        leaderboard[winner] = (
            leaderboard.get(
                winner,
                0
            ) + 1
        )

        save_data()

        bot.send_message(
            ev["chat_id"],
f"""
===========================
 👑 GIVEAWAH WINNERR 👑   |||
===========================
🤝😎🤝😎🤝😎🤝😎🤝😎🤝 |||
===========================
👑 CONGRATULATIONS BRO 👑 |||
=============================
🏆 WINNER: {safe_name(user)} 😎|||
=============================
🎁 PRIZE: {ev['prize']} 🎁              |||
=====================================
🔥 DM THE ADMIN FOR YOUR REWARD 🔥  |||
=====================================
"""
        )

    else:

        bot.send_message(
            ev["chat_id"],
            "❌ NO PLAYERS JOINED"
        )

    # REMOVE JOIN BUTTON
    try:

        bot.edit_message_reply_markup(
            chat_id=ev["chat_id"],
            message_id=ev["message_id"],
            reply_markup=None
        )

    except:
        pass

    events[key] = None

    save_data()

# =========================================================
# GIVEAWAY
# =========================================================

def giveaway(update, context):

    if not is_admin(update):
        return

    prize = "5 ACCOUNTS"

    ev = {
        "title": "🎁 GIVEAWAY EVENT",
        "prize": prize,
        "chat_id": update.effective_chat.id,
        "message_id": None,
        "players": [],
        "start": now(),
        "end": now() + 3600,
        "duration": 3600
    }

    events["giveaway"] = ev

    msg = update.message.reply_text(
        "🎁 STARTING GIVEAWAY..."
    )

    ev["message_id"] = msg.message_id

    save_data()

# =========================================================
# PREMIUM GIVEAWAY
# =========================================================

def premium(update, context):

    if not is_admin(update):
        return

    prize = "10 ACCOUNTS"

    ev = {
        "title": "👑 PREMIUM GIVEAWAY",
        "prize": prize,
        "chat_id": update.effective_chat.id,
        "message_id": None,
        "players": [],
        "start": now(),
        "end": now() + 86400,
        "duration": 86400
    }

    events["premium"] = ev

    msg = update.message.reply_text(
        "👑 STARTING PREMIUM GIVEAWAY..."
    )

    ev["message_id"] = msg.message_id

    save_data()

# =========================================================
# JOIN BUTTONS
# =========================================================

def join_giveaway(update, context):

    q = update.callback_query

    uid = q.from_user.id

    ev = events["giveaway"]

    if ev:

        if uid not in ev["players"]:

            ev["players"].append(uid)

            save_data()

            q.answer(
                "Joined Giveaway!"
            )

        else:

            q.answer(
                "Already Joined 🤣"
            )


def join_premium(update, context):

    q = update.callback_query

    uid = q.from_user.id

    ev = events["premium"]

    if ev:

        if uid not in ev["players"]:

            ev["players"].append(uid)

            save_data()

            q.answer(
                "Joined Premium!"
            )

        else:

            q.answer(
                "Already Joined 🤣"
            )
            
# =========================================================
# QUIZ SYSTEM
# =========================================================

def ask_quiz(
    update,
    context,
    questions,
    title
):

    if not is_admin(update):
        return

    q = random.choice(
        questions
    )

    chat_id = update.effective_chat.id

    quiz_data[chat_id] = {
        "answer": q[1].lower(),
        "end": now() + 20
    }

    msg = update.message.reply_text(
        "⏳ STARTING QUIZ..."
    )

    total = 20

    for remaining in range(
        total,
        0,
        -2
    ):

        bars = (
            "🟩" *
            int(
                (
                    remaining /
                    total
                ) * 10
            )
        )

        bars += (
            "⬜" *
            (
                10 - len(bars)
            )
        )

        try:

            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,

                text=
                "━━━━━━━━━━━━━━━━━━\n"
                f"{title} ANSWER FAST BRO\n"
                "━━━━━━━━━━━━━━━━━━\n"

                "👑 PRIZE: 1ACCOUNT\n"

                "🏆 ONLY ONE WINNER\n"

                "⚡ ANSWER FAST ⚡\n"

                f"❓ {q[0]}\n"

                f"⏳ {remaining}s LEFT\n"

                f"{bars}\n"

                "━━━━━━━━━━━━━━━━━━"
            )

        except:
            pass

        time.sleep(0.3)

        if chat_id not in quiz_data:
            return

    if chat_id in quiz_data:

        del quiz_data[chat_id]

        context.bot.send_message(
            chat_id,
"""
━━━━━━━━━━━━━━━━━━
⏰ TIME'S UP BRO BROO⏰
━━━━━━━━━━━━━━━━━━

✖️✖️✖️✖️✖️✖️✖️✖️✖️
❌ NO ONE ANSWERED❌
✖️✖️✖️✖️✖️✖️✖️✖️✖️

━━━━━━━━━━━━━━━━━━
"""
        )

# =========================================================
# CHECK ANSWER
# =========================================================

def check_answer(update, context):

    chat_id = update.effective_chat.id

    if chat_id not in quiz_data:
        return

    if now() > quiz_data[chat_id]["end"]:
        return

    answer = (
        update.message.text
        .lower()
        .strip()
    )

    if answer == quiz_data[chat_id]["answer"]:

        user = update.message.from_user

        leaderboard[user.id] = (
            leaderboard.get(
                user.id,
                0
            ) + 1
        )

        save_data()

        update.message.reply_text(
f"""
━━━━━━━━━━━━━━━━━━
👑😎 QUIZ WINNER 😎👑
━━━━━━━━━━━━━━━━━━
━━━━━━━━━━━━━━━━━━
👑 CONGRATULATIONS 👑
━━━━━━━━━━━━━━━━━━
🏆 WINNER:{safe_name(user)}🏆
━━━━━━━━━━━━━━━━━━
━━━━━━━━━━━━━━━━━━
🎁 PRIZE:1 ACCOUNT
━━━━━━━━━━━━━━━━━━
━━━━━━━━━━━━━━━━━━
🔥 DM ADMIN FOR REWARD 🔥
━━━━━━━━━━━━━━━━━━
━━━━━━━━━━━━━━━━━━
"""
        )

        del quiz_data[chat_id]

# =========================================================
# QUIZ COMMANDS
# =========================================================

def carquiz(update, context):

    threading.Thread(
        target=ask_quiz,
        args=(
            update,
            context,
            car_q,
            "🚗 CAR QUIZ 🚗\nGOOD LUCK BRO"
        )
    ).start()


def mathquiz(update, context):

    threading.Thread(
        target=ask_quiz,
        args=(
            update,
            context,
            math_q,
            "🧠 MATH QUIZ 🧠\nGOOD LUCK BRO"
        )
    ).start()


def puzzle(update, context):

    threading.Thread(
        target=ask_quiz,
        args=(
            update,
            context,
            puzzle_q,
            "🧩 PUZZLE GAME 🧩\nGOOD LUCK BRO"
        )
    ).start()


def carlogo(update, context):

    threading.Thread(
        target=ask_quiz,
        args=(
            update,
            context,
            logo_q,
            "🚘 CAR LOGO QUIZ 🚘\nGOOD LUCK BRO"
        )
    ).start()
    
# =========================================================
# TAP RACE TOURNAMENT
# =========================================================

def taprace(update, context):

    global tournament_players

    if not is_admin(update):
        return

    tournament_players = []

    keyboard = [[
        InlineKeyboardButton(
            "🏁 JOIN TOURNAMENT (0/20)",
            callback_data="join_taprace"
        )
    ]]

    update.message.reply_text(
"""
━━━━━━━━━━━━━━━━━━
🏁 TAP RACE TOURNAMENT
━━━━━━━━━━━━━━━━━━

⚔️ REAL ELIMINATION
👑 SEMI FINALS
🏆 GRAND FINALS

🔥 TAP FAST TO WIN

👥 MAX PLAYERS: 20

🎁 REWARD: 5 ACCOUNTS

👑 WAIT FOR ADMIN
TO START THE MATCH 👑

━━━━━━━━━━━━━━━━━━
""",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )

# =========================================================
# JOIN TOURNAMENT
# =========================================================

def join_taprace(update, context):

    global tournament_players

    q = update.callback_query

    user = q.from_user

    if user.id in tournament_players:

        q.answer(
            "Already Joined 🤣"
        )

        return

    if len(tournament_players) >= 20:

        q.answer(
            "Tournament Full"
        )

        return

    tournament_players.append(
        user.id
    )

    total = len(
        tournament_players
    )

    keyboard = [[
        InlineKeyboardButton(
            f"🏁 JOIN TOURNAMENT ({total}/20)",
            callback_data="join_taprace"
        )
    ]]

    try:

        q.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

    except:
        pass

    q.answer(
        f"{total}/20 Joined"
    )

# =========================================================
# MANUAL ADMIN START
# =========================================================

def starttap(update, context):

    global match_running

    if not is_admin(update):
        return

    # PREVENT DOUBLE START
    if match_running:

        update.message.reply_text(
            "⚠️ Tournament already running"
        )

        return

    # NEED PLAYERS
    if len(tournament_players) < 2:

        update.message.reply_text(
            "❌ NEED ATLEAST 2 PLAYERS"
        )

        return

    # START TOURNAMENT
    threading.Thread(
        target=start_tournament,
        args=(
            context,
            update.effective_chat.id
        ),
        daemon=True
    ).start()

# =========================================================
# TOURNAMENT ENGINE
# =========================================================

def start_tournament(
    context,
    chat_id
):

    global tournament_players
    global tournament_winners
    global match_running

    match_running = True

    round_num = 1

    while len(
        tournament_players
    ) > 1:

        tournament_winners = []

        context.bot.send_message(
            chat_id,
f"""
━━━━━━━━━━━━━━━━━━
🏆 ROUND {round_num}
━━━━━━━━━━━━━━━━━━
"""
        )

        while len(
            tournament_players
        ) >= 2:

            p1 = tournament_players.pop(0)
            p2 = tournament_players.pop(0)

            winner = run_match(
                context,
                chat_id,
                p1,
                p2
            )

            tournament_winners.append(
                winner
            )

        # AUTO ADVANCE ODD PLAYER
        if len(
            tournament_players
        ) == 1:

            tournament_winners.append(
                tournament_players.pop(0)
            )

        tournament_players = (
            tournament_winners.copy()
        )

        round_num += 1

    # =========================
    # TOURNAMENT CHAMPION
    # =========================

    champion = tournament_players[0]

    user = context.bot.get_chat(
        champion
    )

    leaderboard[champion] = (
        leaderboard.get(
            champion,
            0
        ) + 5
    )

    save_data()

    context.bot.send_message(
        chat_id,
f"""
━━━━━━━━━━━━━━━━━━
👑 TOURNAMENT CHAMPION
━━━━━━━━━━━━━━━━━━

🏆 WINNER:
{safe_name(user)}

🔥 DOMINATED
THE TOURNAMENT 🔥

🎁 WON:
5 ACCOUNTS

👑 DM ADMIN
FOR REWARD 👑

━━━━━━━━━━━━━━━━━━
"""
    )

    # RESET TOURNAMENT
    match_running = False

# =========================================================
# MATCH SYSTEM
# =========================================================

def run_match(context, chat_id, p1, p2):

    global taprace_match
    global taprace_taps
    global taprace_active
    global taprace_started
    global taprace_message_id

    # MATCH STATE
    taprace_active = True
    taprace_started = False

    taprace_match = [p1, p2]

    taprace_taps = {
        p1: 0,
        p2: 0
    }

    # USERS
    u1 = context.bot.get_chat(p1)
    u2 = context.bot.get_chat(p2)

    # BUTTON
    keyboard = [[
        InlineKeyboardButton(
            "🔥 TAP FAST 🔥",
            callback_data="tap_button"
        )
    ]]

    # START MESSAGE
    msg = context.bot.send_message(
        chat_id,
        "⚔️ PREPARING MATCH..."
    )

    taprace_message_id = msg.message_id

    # =========================
    # COUNTDOWN
    # =========================

    countdown = [
        "5️⃣",
        "4️⃣",
        "3️⃣",
        "2️⃣",
        "1️⃣"
    ]

    for num in countdown:

        try:

            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,

                text=
                "━━━━━━━━━━━━━━━━━━\n"
                "⚔️ NEXT MATCH\n"
                "━━━━━━━━━━━━━━━━━━\n\n"

                f"👤 {safe_name(u1)}\n\n"

                "🆚\n\n"

                f"👤 {safe_name(u2)}\n\n"

                f"{num}\n\n"

                "⏳ GET READY...\n"

                "━━━━━━━━━━━━━━━━━━",

                reply_markup=InlineKeyboardMarkup(
                    keyboard
                )
            )

        except BadRequest:
            pass

        except Exception as e:
            print(e)

        time.sleep(1)

    # =========================
    # START GAME
    # =========================

    taprace_started = True

    try:

        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg.message_id,

            text=
            "━━━━━━━━━━━━━━━━━━\n"
            "🔥 GO GO GO 🔥\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            f"👤 {safe_name(u1)}\n"
            "🆚\n"
            f"👤 {safe_name(u2)}\n\n"

            "⚡ TAP FAST NOW ⚡\n"
            "🔥 SPAM THE BUTTON 🔥\n"

            "━━━━━━━━━━━━━━━━━━",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

    except BadRequest:
        pass

    except Exception as e:
        print(e)

    time.sleep(1)

    # =========================
    # MATCH TIMER
    # =========================

    total = 10

    for sec in range(total, -1, -1):

        p1_taps = taprace_taps.get(p1, 0)
        p2_taps = taprace_taps.get(p2, 0)

        max_taps = max(
            p1_taps,
            p2_taps,
            1
        )

        # PLAYER 1 BAR
        p1_fill = int(
            (p1_taps / max_taps) * 10
        )

        p1_bar = (
            "🟩" * p1_fill
        ) + (
            "⬜" * (10 - p1_fill)
        )

        # PLAYER 2 BAR
        p2_fill = int(
            (p2_taps / max_taps) * 10
        )

        p2_bar = (
            "🟦" * p2_fill
        ) + (
            "⬜" * (10 - p2_fill)
        )

        # TIMER BAR
        timer_fill = int(
            (sec / total) * 10
        )

        timer_bar = (
            "🟨" * timer_fill
        ) + (
            "⬜" * (10 - timer_fill)
        )

        try:

            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,

                text=
                "━━━━━━━━━━━━━━━━━━\n"
                "🏁 LIVE TAP RACE\n"
                "━━━━━━━━━━━━━━━━━━\n\n"

                f"👤 {safe_name(u1)}\n\n"

                f"🔥 {p1_taps} TAPS\n"

                f"{p1_bar}\n\n"

                "🆚\n\n"

                f"👤 {safe_name(u2)}\n\n"

                f"🔥 {p2_taps} TAPS\n"

                f"{p2_bar}\n\n"

                f"⏳ {sec}s LEFT\n"

                f"{timer_bar}\n\n"

                "⚡ TAP FAST NOW ⚡\n"
                "🔥 SPAM THE BUTTON 🔥\n"

                "━━━━━━━━━━━━━━━━━━",

                reply_markup=InlineKeyboardMarkup(
                    keyboard
                )
            )

        except:
            pass

        time.sleep(0.8)

    # =========================
    # END MATCH
    # =========================

    taprace_active = False
    taprace_started = False

    p1_final = taprace_taps.get(p1, 0)
    p2_final = taprace_taps.get(p2, 0)

    # WINNER
    if p1_final >= p2_final:
        winner = p1
        loser = p2
    else:
        winner = p2
        loser = p1

    w_user = context.bot.get_chat(
        winner
    )

    l_user = context.bot.get_chat(
        loser
    )

    # FINAL BARS
    max_final = max(
        p1_final,
        p2_final,
        1
    )

    p1_final_fill = int(
        (p1_final / max_final) * 10
    )

    p2_final_fill = int(
        (p2_final / max_final) * 10
    )

    p1_final_bar = (
        "🟩" * p1_final_fill
    ) + (
        "⬜" * (10 - p1_final_fill)
    )

    p2_final_bar = (
        "🟦" * p2_final_fill
    ) + (
        "⬜" * (10 - p2_final_fill)
    )

    try:

        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg.message_id,

            text=
            "━━━━━━━━━━━━━━━━━━\n"
            "🏆 MATCH RESULT\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            f"👤 {safe_name(u1)}\n"
            f"🔥 {p1_final} taps\n"
            f"{p1_final_bar}\n\n"

            "🆚\n\n"

            f"👤 {safe_name(u2)}\n"
            f"🔥 {p2_final} taps\n"
            f"{p2_final_bar}\n\n"

            f"👑 WINNER:\n"
            f"{safe_name(w_user)}\n\n"

            f"💀 ELIMINATED:\n"
            f"{safe_name(l_user)}\n\n"

            "━━━━━━━━━━━━━━━━━━"
        )

    except BadRequest:
        pass

    except Exception as e:
        print(e)

    return winner

# =========================================================
# TAP BUTTON
# =========================================================

def tap_button(update, context):

    global taprace_active
    global taprace_started
    global taprace_match
    global taprace_taps
    global last_tap

    q = update.callback_query

    uid = q.from_user.id

    # MATCH ENDED
    if not taprace_active:

        q.answer(
            "🏁 Match ended!"
        )

        return

    # WAIT FOR GO
    if not taprace_started:

        q.answer(
            "⏳ Wait for GO!"
        )

        return

    # OUTSIDER
    if uid not in taprace_match:

        q.answer(
            "❌ NOT YOUR MATCH"
        )

        return

    # ANTI SPAM SYSTEM
    current = time.time()

    if uid in last_tap:

        if current - last_tap[uid] < 0.03:
            return

    last_tap[uid] = current

    # SAFETY
    if uid not in taprace_taps:

        taprace_taps[uid] = 0

    # ADD TAP
    taprace_taps[uid] += 1

    # LIGHT RESPONSE
    try:

        q.answer()

    except BadRequest:
        pass

    except Exception as e:
        print(e)

# =========================================================
# MAIN
# =========================================================

updater = Updater(
    TOKEN,
    use_context=True
)

dp = updater.dispatcher

# =========================================================
# COMMANDS
# =========================================================

dp.add_handler(
    CommandHandler(
        "start",
        start
    )
)

dp.add_handler(
    CommandHandler(
        "profile",
        profile
    )
)

dp.add_handler(
    CommandHandler(
        "leaderboard",
        leaderboard_cmd
    )
)

dp.add_handler(
    CommandHandler(
        "giveaway",
        giveaway
    )
)

dp.add_handler(
    CommandHandler(
        "premium",
        premium
    )
)

dp.add_handler(
    CommandHandler(
        "carquiz",
        carquiz
    )
)

dp.add_handler(
    CommandHandler(
        "mathquiz",
        mathquiz
    )
)

dp.add_handler(
    CommandHandler(
        "puzzle",
        puzzle
    )
)

dp.add_handler(
    CommandHandler(
        "carlogo",
        carlogo
    )
)

dp.add_handler(
    CommandHandler(
        "taprace",
        taprace
    )
)

dp.add_handler(
    CommandHandler(
        "starttap",
        starttap
    )
)

# =========================================================
# BUTTONS
# =========================================================

dp.add_handler(
    CallbackQueryHandler(
        join_giveaway,
        pattern="join_giveaway"
    )
)

dp.add_handler(
    CallbackQueryHandler(
        join_premium,
        pattern="join_premium"
    )
)

dp.add_handler(
    CallbackQueryHandler(
        join_taprace,
        pattern="join_taprace"
    )
)

dp.add_handler(
    CallbackQueryHandler(
        tap_button,
        pattern="tap_button"
    )
)

# =========================================================
# ANSWERS
# =========================================================

dp.add_handler(
    MessageHandler(
        Filters.text &
        ~Filters.command,
        check_answer
    )
)

# =========================================================
# AUTO TIMER THREAD
# =========================================================

# REFRESH ACTIVE EVENTS
for key in ["giveaway", "premium"]:

    ev = events.get(key)

    if ev:

        remaining = ev["end"] - now()

        if remaining > 0:

            try:

                update_event(
                    updater.bot,
                    key,
                    remaining
                )

            except:
                pass

threading.Thread(
    target=timer_loop,
    args=(updater.bot,),
    daemon=True
).start()

# =========================================================
# BOT START
# =========================================================

print("━━━━━━━━━━━━━━━━━━")
print("🔥 BOT RUNNING 🔥")
print("━━━━━━━━━━━━━━━━━━")

updater.start_polling()

updater.idle()
