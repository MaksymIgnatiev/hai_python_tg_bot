import telebot
import random 

from data import TOKEN 
from telebot import types


bot = telebot.TeleBot(TOKEN)
games: dict[int, dict[str, str | int | set[str]]] = {}

with open("words.txt", "r") as file:
    word_list = [line.strip() for line in file]

def start_new_game(user_id):
    word = random.choice(word_list).lower()
    hidden_word = "_" * len(word)
    games[user_id] = {
        "word": word,
        "h_word": hidden_word,
        "att": 6,
        "letters": set()
    }
    return games[user_id]


# comment

@bot.message_handler(commands=["start"])
def start_command(message):
    bot.send_message(message.chat.id,
                     "Привіт. Я Telegram бот, що працює на [Python](https://www.python.org/) бібліотеці [telebot](https://pypi.org/project/telebot/).\n\n" + \
                            "Що я можу робити:\n" + \
                            "/start - вивести це повідомлення\n" + \
                            "/help - вивести всі доступні команди\n" + \
                            "/game - почати нову гру (якщо гра не почата)\n" 
                     ,
                    "Markdown",
                    link_preview_options=types.LinkPreviewOptions(True)
					)

@bot.message_handler(commands=["game"])
def hangman_command(message):
    game_state = start_new_game(message.from_user.id)
    bot.send_message(message.chat.id, f'Гра почалась! Загадане слово: {game_state["h_word"]}\n'
                                      f'У вас е {game_state["att"]} спроб. Надішліть одну літеру.')

@bot.message_handler(func=lambda message: message.from_user.id in games)
def handle_guess(message):
    game_state = games[message.from_user.id]
    letter = message.text.lower()

@bot.message_handler()
def message(msg: types.Message):
    bot.send_message(msg.chat.id, f"Ypu wrote:\n {msg.text}") 

if __name__ == "__main__":
    try:
        print("\033[32mBot is running!\033[0m")
        bot.polling(none_stop=True)

    except KeyboardInterrupt:
        print("\033[31mBot stopped!\033[0m")
