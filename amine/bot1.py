import telebot
import random as r

# Инициализация бота с действительным API-токеном
TOKEN = "7586521691:AAG8lIeGbdm1ysVAxVCdesg1EJIqpVdqu9c"
bot = telebot.TeleBot("7586521691:AAG8lIeGbdm1ysVAxVCdesg1EJIqpVdqu9c")

# Хранение состояния игры для каждого пользователя
game_data = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing? Send /guess to start a game.")

@bot.message_handler(commands=['guess'])
def gamestart(message):
    chat_id = message.chat.id
    # Генерация случайного числа и сохранение его в словарь
    game_data[chat_id] = r.randint(1, 10)
    bot.send_message(chat_id, 'I chose a random number from 1 to 10, will you be able to guess it?')

@bot.message_handler(func=lambda message: True)
def guess_number(message):
    chat_id = message.chat.id
    # Проверка, есть ли игра для текущего пользователя
    if chat_id not in game_data:
        bot.send_message(chat_id, "Please start a new game by sending /guess")
        return

    try:
        # Преобразование текста в число
        guess = int(message.text)
    except ValueError:
        bot.reply_to(message, "Please enter a valid number.")
        return

    # Сравнение с загаданным числом
    n = game_data[chat_id]
    if guess > 10:
        bot.reply_to(message, "Wtf bro? from 10 and down...")
    elif guess < 1:
            bot.reply_to(message, "Wtf bro?? from 1 and more...")
    elif guess > n:
        bot.reply_to(message, "Less! Try a lower number.")
    elif guess < n:
        bot.reply_to(message, "More! Try a higher number.")
    else:
        bot.reply_to(message, f"Congratulations! You've guessed the correct number: {n}")
        bot.send_message(chat_id, "To play again, send /guess")
        # Удаление данных игры после окончания
        del game_data[chat_id]

# Запуск бота
bot.infinity_polling()