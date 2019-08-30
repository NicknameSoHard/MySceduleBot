import telebot

from utils.spreadsheets_worker import SpreadsheetsWorker
from config import bot_config

bot = telebot.TeleBot(bot_config.TOKEN)
telebot.apihelper.proxy = bot_config.PROXY
ssw = SpreadsheetsWorker()


@bot.message_handler()
def get_text_messages(message):
    user_id = message.chat.id
    markup = telebot.types.ReplyKeyboardMarkup(#one_time_keyboard=True,
                                               resize_keyboard=True,
                                               row_width=2)
    button1 = telebot.types.KeyboardButton('Новая трата')
    button2 = telebot.types.KeyboardButton('Новый доход')
    markup.add(button1, button2)
    msg = bot.send_message(user_id, 'Что бы вы хотели внести?', reply_markup=markup)
    bot.register_next_step_handler(msg, new_operation)


def new_operation(message):
    user_id = message.chat.id
    if message.text == 'Новая трата':
        category_type = 'outlay'
    elif message.text == 'Новый доход':
        category_type = 'income'
    else:
        bot.send_message(user_id, 'Выберите один из вариантов с клавиатуры.')
        return False
    category_list = ssw.get_category_list(category_type)

    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                               resize_keyboard=True,
                                               row_width=len(category_list))
    buttons = []
    for category in category_list:
        buttons.append(telebot.types.KeyboardButton(category))
    markup.add(*buttons[:int(len(buttons)/2)])
    markup.add(*buttons[int(len(buttons)/2):])
    msg = bot.send_message(user_id, 'Выберите категорию.', reply_markup=markup)
    category = None
    amount = None
    bot.register_next_step_handler(msg, get_category_or_amount,
                                   category_type,
                                   category_list, category, amount)


def get_category_or_amount(message, category_type, category_list, category, amount):
    user_id = message.chat.id
    if message.text in category_list:
        category = message.text
        if amount is None:
            result_message = 'Теперь введите сумму:'
    else:
        try:
            amount = int(message.text)
            if category is None:
                result_message = 'Теперь введите категорию.'
        except ValueError:
            result_message = 'Ошибка. Введите или выберете еще раз.'
            new_operation(message)

    if amount is not None and category is not None:
        result = ssw.new_value_for_day(category_type, category, amount)
        if result:
            result_message = 'Успешно записано в табличку!'
        else:
            result_message = 'Ошибка сохранения.'
        bot.send_message(user_id, result_message)
        get_text_messages(message)
    else:
        msg = bot.send_message(user_id, result_message)
        bot.register_next_step_handler(msg, get_category_or_amount,
                                       category_type, category_list, category, amount)


if __name__ == '__main__':
  bot.polling(none_stop=True)
