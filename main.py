import telebot
import re
import random 
import json

from data import TOKEN 
from telebot import types

bot = telebot.TeleBot(TOKEN)

games: dict[int, dict[str, str | int | list[str] | list[int]]] = {}

with open("words.txt", "r") as file:
    word_list = [line.strip() for line in file]


def start_new_game(user_id):
    games[user_id] = {
        "word": (word := random.choice(word_list).lower()),
        "h_word": ["_"] * len(word),
        "att": 6,
        "letters": [],
        "msgs": []
    }
    return games[user_id]


def format_message(obj: dict[str, str | int | list[str]]):
    return f'Залишилось спроб: {obj["att"]}\n\nСлово:\n\n{" ".join(obj["h_word"])}\n\nВикористані літери:\n\n{" ".join(obj["letters"])}'


def update_message(obj, chatId: int):
    bot.edit_message_text(format_message(obj), chatId, obj["msg"])



@bot.message_handler(commands=["start"])
def start_command(msg: types.Message):
    bot.send_message(msg.chat.id,
                     "Привіт. Я телеграм бот для гри в [шибеницю](https://uk.m.wikipedia.org/wiki/%D0%A8%D0%B8%D0%B1%D0%B5%D0%BD%D0%B8%D1%86%D1%8F_(%D0%B3%D1%80%D0%B0)) написаний на [Python](https://www.python.org/) бібліотеці [telebot](https://pypi.org/project/telebot/).\n\n" + \
                             "Для подробиць використовуйте команду: /help"
                     ,
                    "Markdown",
                    link_preview_options=types.LinkPreviewOptions(True)
                    )




@bot.message_handler(commands=["game"])
def hangman_command(msg: types.Message):
    if msg.from_user.id not in games:
        user = start_new_game(msg.from_user.id)
        bot.send_message(msg.chat.id, f'Гра почалась! Надішліть одну літеру.\n\nДля подробиць використовуйте команду: /help')
        user["msg"] = bot.send_message(msg.chat.id, format_message(user)).message_id
    else:
        bot.send_message(msg.chat.id, "Ви вже почали гру. Якщо вам нужна допомога, відправьте команду: /help")



@bot.message_handler(func=lambda msg: msg.from_user.id in games and msg.text)
def handle_guess(msg: types.Message):
    chatId = msg.chat.id
    userId = msg.from_user.id
    user = games[userId]
    text = msg.text.lower().strip()

    if text in ["/stop", "/exit"]:
        del games[userId]
        return bot.send_message(chatId, "Ваша гра була закінчена.")

    if text == "/help":
        return bot.send_message(chatId,
                                    "Допомога:\n\n" + \
                                    "/stop / /exit - закінчити гру\n" + \
                                    "/help - відправити це повідомленя\n" + \
                                    "/resend - надіслати повідомлення з відгадуванням ще раз"
                                )

    if text == "/resend":
        user["msg"] = bot.send_message(chatId, format_message(user)).message_id
        return

    letter = text

    if len(letter) != 1:
        bot.delete_message(chatId, msg.message_id)
        user["msgs"].append(bot.send_message(chatId, "Надішліть лише одну літеру!").message_id)
        return

    if re.match(r"[^а-яіїєґейь]", letter):
        bot.delete_message(chatId, msg.message_id)
        user["msgs"].append(bot.send_message(chatId, "Літера має бути з українського алфавіту").message_id)
        return
    
    bot.delete_message(chatId, msg.message_id)

    if len(user["msgs"]) != 0:
        try:
            for id in user["msgs"]:
                bot.delete_message(chatId, id)
        except Exception: pass

    if letter in user["word"]:
        if letter not in user["h_word"]:
            for i, l in enumerate(user["word"]):
                if l == letter: user["h_word"][i] = l
            update_message(user, chatId)
        if user["word"] == "".join(user["h_word"]):
            bot.send_message(chatId, "Вітаю!  Ви відгадали слово.  Гра закінчена.")
            del games[userId]

    elif letter not in user["letters"]:
        user["att"] -= 1
        user["letters"].append(letter)
        update_message(user, chatId)
        if not user["att"]:
            bot.send_message(chatId, f"Вы програли. Вашим словом було: {user['word']}\n\nГра закінчена.")
            del games[userId]


@bot.message_handler(commands=["help"])
def start_command(msg: types.Message):
    bot.send_message(msg.chat.id,
                        "Допомога з боту:\n\n" + \
                        "/start - запуск/перезапуск бота\n" + \
                        "/help - вивести це повідомлення\n" + \
                        "/game - почати нову гру (якщо ще не була розпочата)\n\n" + \
                        "Під час гри також будуть доступні інші команди.  Їх також можна дізнатися відіславши команду /help, але вже під час гри."
                     )


@bot.message_handler()
def message(msg: types.Message):
    bot.send_message(msg.chat.id, f"Це не валідна команда для бота.  Список доступних команд можна дізнатися надіславши команду: /help") 

if __name__ == "__main__":
    try:
        print("\033[32mBot is running!\033[0m")
        bot.polling(none_stop=True)

    except KeyboardInterrupt:
        print("\033[31mBot stopped!\033[0m")
