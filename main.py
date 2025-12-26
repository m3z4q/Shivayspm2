import asyncio
import random
import hashlib
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# -------- CONFIG --------
BOT_TOKEN = "8209118332:AAE0Y9vLNcTRGHTOQqdowKKhpqiYZFDOjd0"

# ONLY 2 OWNERS
OWNERS = {8453291493, 8295675309}

# 🔥 NEW MASTER EMOJI POOL (DIFFERENT FROM FIRST BOT)
MASTER_EMOJIS = [
    "🩸","🕷️","🦂","🦇","🧛","🧟","🧬","⚔️","🗡️","🏴‍☠️",
    "🌑","🌘","🌒","🌪️","☄️","🪓","🪦","🕸️","🩻","👁️‍🗨️"
]

# -------- AUTO EMOJI GENERATOR (TOKEN BASED) --------
def generate_emojis(token: str):
    hash_val = hashlib.sha256(token.encode()).hexdigest()
    random.seed(hash_val)
    emojis = MASTER_EMOJIS.copy()
    random.shuffle(emojis)
    return emojis[:8]  # unique emoji set per bot

EMOJIS = generate_emojis(BOT_TOKEN)

# -------- STORAGE --------
gcnc_tasks = {}

# -------- HELPERS --------
def is_owner(user_id: int) -> bool:
    return user_id in OWNERS

# -------- COMMANDS --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("❌ Private bot. Access denied.")
    await update.message.reply_text("🤖 Bot Online\nUse /help")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    await update.message.reply_text(
        "/spam <count> <text>\n"
        "/gcnc <group_name>\n"
        "/stopgcnc"
    )

async def spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_owner(user.id):
        return await update.message.reply_text("❌ Access denied.")

    if len(context.args) < 2:
        return await update.message.reply_text("Usage: /spam <count> <text>")

    try:
        count = int(context.args[0])
        text = " ".join(context.args[1:])
    except:
        return await update.message.reply_text("Invalid arguments.")

    for _ in range(count):
        await update.message.reply_text(text)
        await asyncio.sleep(0.15)

async def gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if not is_owner(user.id):
        return await update.message.reply_text("❌ Access denied.")

    if chat.type not in ["group", "supergroup"]:
        return await update.message.reply_text("Group only command.")

    if not context.args:
        return await update.message.reply_text("Usage: /gcnc <group_name>")

    base = " ".join(context.args)

    async def loop():
        while True:
            try:
                emoji = random.choice(EMOJIS)
                await chat.set_title(f"{emoji} {base}")
                await asyncio.sleep(2)
            except:
                await asyncio.sleep(5)

    if chat.id in gcnc_tasks:
        gcnc_tasks[chat.id].cancel()

    gcnc_tasks[chat.id] = asyncio.create_task(loop())
    await update.message.reply_text("✅ GCNC started (emoji auto-rotate)")

async def stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if not is_owner(user.id):
        return await update.message.reply_text("❌ Access denied.")

    task = gcnc_tasks.pop(chat.id, None)
    if task:
        task.cancel()
        await update.message.reply_text("🛑 GCNC stopped")
    else:
        await update.message.reply_text("No GCNC running.")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        return
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"👋 Welcome {member.mention_html()}!",
            parse_mode="HTML"
        )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_owner(update.effective_user.id):
        await update.message.reply_text("❓ Unknown command.")

# -------- MAIN --------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("spam", spam))
    app.add_handler(CommandHandler("gcnc", gcnc))
    app.add_handler(CommandHandler("stopgcnc", stopgcnc))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    app.run_polling()

if __name__ == "__main__":
    main()