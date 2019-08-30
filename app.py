import telebot

from utils.spreadsheets_worker import SpreadsheetsWorker
from config import bot_config

bot = telebot.TeleBot(bot_config.TOKEN)
telebot.apihelper.proxy = bot_config.PROXY
ssw = SpreadsheetsWorker()


@bot.message_handler()
def get_text_messages(message):
    user_id = message.chat.id
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                               resize_keyboard=True,
                                               row_width=2)
    button1 = telebot.types.KeyboardButton('Новая трата')
    button2 = telebot.types.KeyboardButton('Новый доход')
    markup.add(button1, button2)
    msg = bot.send_message(user_id, 'Что бы вы хотели внести?', reply_markup=markup)
    bot.register_next_step_handler(msg, user_button_enter)


def new_outlay(message):
    user_id = message.chat.id
    category_list = ssw.get_category_list()
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                               resize_keyboard=True,
                                               row_width=len(category_list))
    buttons = []
    for category in category_list:
        buttons.append(telebot.types.KeyboardButton(category))
    markup.add(*buttons[:int(len(buttons)/2)])
    markup.add(*buttons[int(len(buttons)/2):])
    msg = bot.send_message(user_id,
                           'Выберите категорию затраты, А после напишите сумму',
                           reply_markup=markup)
    category = None
    amount = None
    bot.register_next_step_handler(msg, get_category_or_amount, category_list, category, amount)


def get_category_or_amount(message, category_list, category, amount):
    user_id = message.chat.id
    if message.text in category_list:
        category = message.text
        if amount is None:
            msg = bot.send_message(user_id, 'Теперь введите число')
    else:
        try:
            amount = int(message.text)
            if category is None:
                msg = bot.send_message(user_id, 'Теперь введите категорию')
        except ValueError:
            msg = bot.send_message(user_id, 'Ошибка. Введите или выберете еще раз.')
            new_outlay(message)
    if amount is not None and category is not None:
        result = ssw.new_values_for_day(category=category, value=amount)
        if result:
            bot.send_message(user_id, 'Успешно записано в табличку!')
            get_text_messages(message)
        else:
            bot.send_message(user_id, 'Ошибка сохранения.')
    else:
        bot.register_next_step_handler(msg, get_category_or_amount, category_list, category, amount)


def new_income(message):
    pass


def user_button_enter(message):
    if message.text == 'Новая трата':
        new_outlay(message)
    if message.text == 'Новый доход':
        new_income(message)


if __name__ == '__main__':
  bot.polling(none_stop=True)
