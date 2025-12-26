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
from telegram.error import RetryAfter, BadRequest

# -------- CONFIG --------
BOT_TOKEN = "8209118332:AAE0Y9vLNcTRGHTOQqdowKKhpqiYZFDOjd0"

# ONLY 2 OWNERS
OWNERS = {8453291493, 8295675309}

# SECOND BOT OFFSET
OFFSET = 0.5

# 🧿 SECOND BOT EMOJI LIST (DIFFERENT)
MASTER_EMOJIS = [
    "🌀","💫","✨","⚡","🌪️","☄️","🌈","🎯",
    "😈","👁️","🧠","🦂","🦅","🐺","🩸","☠️"
]

# -------- AUTO EMOJI GENERATOR --------
def generate_emojis(token: str):
    h = hashlib.sha256(token.encode()).hexdigest()
    random.seed(h)
    emojis = MASTER_EMOJIS.copy()
    random.shuffle(emojis)
    return emojis

EMOJIS = generate_emojis(BOT_TOKEN)

# -------- STORAGE --------
gcnc_tasks = {}

# -------- HELPERS --------
def is_owner(user_id: int) -> bool:
    return user_id in OWNERS

# -------- COMMANDS --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    await update.message.reply_text("🤖 Second Bot Online\nUse /help")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    await update.message.reply_text(
        "/spam <count> <text>\n"
        "/gcnc <group_name>\n"
        "/stopgcnc"
    )

async def spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    if len(context.args) < 2:
        return

    count = int(context.args[0])
    text = " ".join(context.args[1:])

    for _ in range(count):
        await update.message.reply_text(text)
        await asyncio.sleep(0.12)

# -------- GCNC (FOLLOWER – NON-STOP) --------
async def gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        return

    if not context.args:
        return await update.message.reply_text("Usage: /gcnc <group_name>")

    base = " ".join(context.args)

    async def loop():
        # follower offset
        await asyncio.sleep(OFFSET)
        idx = 0

        while True:
            try:
                emoji = EMOJIS[idx % len(EMOJIS)]
                idx += 1

                await chat.set_title(f"{emoji} {base}")

                # FAST + STABLE
                await asyncio.sleep(0.65)

            except RetryAfter as e:
                # forced wait → auto resume
                await asyncio.sleep(e.retry_after + 0.5)

            except BadRequest:
                await asyncio.sleep(0.2)

            except asyncio.CancelledError:
                break

            except Exception:
                await asyncio.sleep(1)

    if chat.id in gcnc_tasks:
        gcnc_tasks[chat.id].cancel()

    gcnc_tasks[chat.id] = context.application.create_task(loop())
    await update.message.reply_text("✅ GCNC started (SECOND BOT – FOLLOWER MODE)")

async def stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task = gcnc_tasks.pop(update.effective_chat.id, None)
    if task:
        task.cancel()
        await update.message.reply_text("🛑 GCNC stopped")

# -------- MAIN --------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("spam", spam))
    app.add_handler(CommandHandler("gcnc", gcnc))
    app.add_handler(CommandHandler("stopgcnc", stopgcnc))
    app.add_handler(MessageHandler(filters.COMMAND, lambda u, c: None))

    app.run_polling()

if __name__ == "__main__":
    main()
