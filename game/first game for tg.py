from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)
from random import randint, choice
import asyncio

import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

CHOOSING_ACTION = range(1)

# --- Игра ---

player = {
    'name': 'Hero',
    'hp': 100,
    'max_hp': 100,
    'attack': 20,
    'heal': 15
}

monster_templates = [
    {'name': 'Гоблин', 'hp': 80, 'attack': 12},
    {'name': 'Скелет', 'hp': 75, 'attack': 10},
    {'name': 'Орк', 'hp': 120, 'attack': 15}
]

monster = {}

def new_monster():
    template = choice(monster_templates)
    return {
        'name': template['name'],
        'hp': template['hp'],
        'attack': template['attack']
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global player, monster
    player['hp'] = player['max_hp']
    monster = new_monster()
    await update.message.reply_text(
        f"⚔️ Ты встретил {monster['name']}! Приготовься к бою!\n\n"
        f"Твои HP: {player['hp']} | HP врага: {monster['hp']}\n"
        "Напиши 1, чтобы атаковать, или 2 — чтобы лечиться."
    )
    return CHOOSING_ACTION

async def player_turn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global player, monster
    text = update.message.text.strip()

    if text not in ["1", "2"]:
        await update.message.reply_text("Пиши только 1 (атака) или 2 (лечение).")
        return CHOOSING_ACTION

    if text == "1":
        damage = randint(player['attack'] - 5, player['attack'] + 5)
        monster['hp'] -= damage
        await update.message.reply_text(f"Ты ударил {monster['name']} и нанёс {damage} урона!")
    elif text == "2":
        heal = randint(player['heal'] - 3, player['heal'] + 3)
        player['hp'] = min(player['max_hp'], player['hp'] + heal)
        await update.message.reply_text(f"Ты лечишься на {heal} HP!")

    await asyncio.sleep(1)

    if monster['hp'] <= 0:
        await update.message.reply_text(f"🎉 Ты победил {monster['name']}!")
        monster = new_monster()
        await update.message.reply_text(
            f"⚔️ Новый враг: {monster['name']}!\n"
            f"Твои HP: {player['hp']} | HP врага: {monster['hp']}\n"
            "1 — Атака\n2 — Лечение"
        )
        return CHOOSING_ACTION

    # Атака монстра
    damage = randint(monster['attack'] - 3, monster['attack'] + 3)
    player['hp'] -= damage
    await update.message.reply_text(f"{monster['name']} атакует и наносит тебе {damage} урона!")

    if player['hp'] <= 0:
        await update.message.reply_text("💀 Ты погиб в бою... /start чтобы начать сначала.")
        return ConversationHandler.END

    await update.message.reply_text(
        f"Твои HP: {player['hp']} | HP врага: {monster['hp']}\n"
        "1 — Атака\n2 — Лечение"
    )
    return CHOOSING_ACTION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Игра окончена. Напиши /start, чтобы начать заново.")
    return ConversationHandler.END

# --- Запуск бота ---

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, player_turn)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("Бот запущен!")
    app.run_polling()
