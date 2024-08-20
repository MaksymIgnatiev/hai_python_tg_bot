import re
import random 
from data import TOKEN 
from telebot import TeleBot
from telebot.types import BotCommand, InputMediaPhoto, InputFile, Message
from dataclasses import dataclass

bot = TeleBot(TOKEN)

gg_sticker = "CAACAgIAAxkBAAICfmbEZfIkgIbghUmJPpHdSXgbdT-hAAKLNgACo69AS-Ey4CvXH-6rNQQ"
go_sticker = "CAACAgIAAxkBAAICf2bEZgwq6_-DWTEVqzaEv8cEUZRwAALzAANWnb0KahvrxMf6lv41BA"
hi_sticker = "CAACAgIAAxkBAAICgGbEZ-NT0_TebhcVBbE8RwuYwL-wAALGAQACFkJrCkoj1PTJ23lHNQQ"
chill_sticker = "CAACAgIAAxkBAAICo2bEbLVMyyXukqeBnBkUUBnKs9gMAAKIAAMWQmsKW_Cgofh5AAElNQQ"

@dataclass
class User:
    word: str
    h_word: list[str]
    att: int
    letters: list[str]
    msgs: list[int]
    msg: int

games: dict[int, User] = {}
pics_folder = "pics"

commands = [
            BotCommand("start", "Запустити бота"), 
            BotCommand("help", "Допомога з боту/грі"), 
            BotCommand("game", "Почати нову гру"), 
            BotCommand("resend", "Надіслати повідомлення з відгадуванням ще раз"), 
            BotCommand("stop", "Закінчити гру"), 
            BotCommand("exit", "Закінчити гру"), 
            ]

bot.set_my_commands(commands)

with open("words.txt", "r") as file: word_list = [line.strip().lower() for line in file]


def start_new_game(user_id: int):
    games[user_id] = User(word=(word := random.choice(word_list)), h_word=["_"] * len(word), att=6, letters=[], msgs=[], msg=0)
    return games[user_id]


def format_message(obj: User): return f'Залишилось спроб: {obj.att}\n\nСлово:\n\n{" ".join(obj.h_word)}{f"""\n\nВикористані літери:\n\n{" ".join(obj.letters)}""" if obj.letters else ""}'


def update_message(obj: User, chatId: int): bot.edit_message_media(InputMediaPhoto(InputFile(open(f'{pics_folder}/{obj.att}.png', 'rb'), f'{obj.att}.png'), format_message(obj)), chatId, obj.msg)


@bot.message_handler(commands=["start"])
def start_command(msg: Message):
    bot.send_sticker(msg.chat.id, hi_sticker)
    bot.send_message(msg.chat.id, "Привіт\\. Я телеграм бот для гри в [шибеницю](https://uk.m.wikipedia.org/wiki/%D0%A8%D0%B8%D0%B1%D0%B5%D0%BD%D0%B8%D1%86%D1%8F_\\(%D0%B3%D1%80%D0%B0\\)) написаний на [Python](https://www.python.org/) бібліотеці [telebot](https://pypi.org/project/telebot/)\\.\n\nДля подробиць використовуйте команду: /help", "MarkdownV2", disable_web_page_preview=True)


@bot.message_handler(commands=["game"])
def game_command(msg: Message):
    if not msg.from_user: return
    if msg.from_user.id not in games:
        user = start_new_game(msg.from_user.id)
        bot.send_message(msg.chat.id, f'Гра почалась! Надішліть одну літеру.\n\nДля подробиць використовуйте команду: /help')
        user.msg = bot.send_photo(msg.chat.id, open(f'{pics_folder}/{user.att}.png', 'rb'), format_message(user)).message_id
    else: bot.send_message(msg.chat.id, "Ви вже почали гру. Якщо вам нужна допомога, відправьте команду: /help")


@bot.message_handler(func=lambda msg: msg.from_user.id in games and msg.text)
def handle_guess(msg: Message):
    if not msg.text or not msg.from_user: return
    chatId, userId, user, text = msg.chat.id, msg.from_user.id, games[msg.chat.id], msg.text.lower().strip()

    if text in ["/stop", "/exit"]:
        del games[userId]
        bot.send_sticker(chatId, chill_sticker)
        return bot.send_message(chatId, "Ваша гра була закінчена.")

    if text == "/help": return bot.send_message(chatId, "Допомога:\n\n/stop / /exit - закінчити гру\n/help - відправити це повідомленя\n/resend - надіслати повідомлення з відгадуванням ще раз")

    if text == "/resend": return user.__setattr__("msg", bot.send_photo(chatId, open(f'{pics_folder}/{user.att}.png', 'rb'), format_message(user)).message_id)

    if len(text) != 1: return (bot.delete_message(chatId, msg.message_id), user.msgs.append(bot.send_message(chatId, "Надішліть лише одну літеру!").message_id))

    if re.match(r"[^а-яіїєґейь]", text): return (bot.delete_message(chatId, msg.message_id), user.msgs.append(bot.send_message(chatId, "Літера має бути з українського алфавіту").message_id))
    
    bot.delete_message(chatId, msg.message_id)

    if user.msgs:
        try:
            for id in user.msgs: bot.delete_message(chatId, id)
        except Exception: pass

    if text in user.word:
        if text not in user.h_word:
            for i, l in enumerate(user.word):
                if l == text: user.h_word[i] = l
            update_message(user, chatId)
        if user.word == "".join(user.h_word):
            bot.send_sticker(chatId, gg_sticker)
            bot.send_message(chatId, "Вітаю!  Ви відгадали слово.  Гра закінчена.")
            del games[userId]

    elif text not in user.letters:
        user.att -= 1
        user.letters.append(text)
        update_message(user, chatId)
        if not user.att:
            bot.send_sticker(chatId, go_sticker)
            bot.send_message(chatId, f'Вы програли. Вашим словом було: {user.word}\n\nГра закінчена.')
            del games[userId]


@bot.message_handler(commands=["help"])
def help_command(msg: Message): bot.send_message(msg.chat.id, "Допомога з боту:\n\n/start - запуск/перезапуск бота\n/help - вивести це повідомлення\n/game - почати нову гру (якщо ще не була розпочата)\n\nПід час гри також будуть доступні інші команди. Їх також можна дізнатися відіславши команду /help, але вже під час гри.")


@bot.message_handler()
def message(msg: Message): bot.send_message(msg.chat.id, f"Це не валідна команда для бота.  Список доступних команд можна дізнатися надіславши команду: /help") 

if __name__ == "__main__":
    try:
        print("\033[32mBot is running!\033[0m")
        bot.polling(non_stop=True)
    except KeyboardInterrupt:
        print("\033[31mBot stopped!\033[0m")
