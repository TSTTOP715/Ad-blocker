import telebot
from config import BOT_TOKEN
from logic import (
    init_db,
    is_link, 
    contains_telegram_entities, 
    is_admin, 
    add_banned_word, 
    remove_banned_word, 
    get_banned_words
)

bot = telebot.TeleBot(BOT_TOKEN)

init_db()

@bot.message_handler(commands=['addword'])
def handle_add_word(message):
    if message.chat.type in ['group', 'supergroup']:
        if not is_admin(bot, message.chat.id, message.from_user.id):
            return
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            word = args[1]
            if add_banned_word(message.chat.id, word):
                bot.reply_to(message, f"слово '{word}' добавлено в список запрещенных")
            else:
                bot.reply_to(message, f"такое слово '{word}' уже есть в списке запрещенных")
        else:
            bot.reply_to(message, "использовать /addword (слово)")

@bot.message_handler(commands=['delword'])
def handle_del_word(message):
    if message.chat.type in ['group', 'supergroup']:
        if not is_admin(bot, message.chat.id, message.from_user.id):
            return
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            word = args[1]
            if remove_banned_word(message.chat.id, word):
                bot.reply_to(message, f"Слово '{word}' удалено из списка запрещенных")
            else:
                bot.reply_to(message, "Слово не найдено в списке")
        else:
            bot.reply_to(message, "Использовать /delword (слово)")

@bot.message_handler(commands=['words'])
def handle_list_words(message):
    if message.chat.type in ['group', 'supergroup']:
        if not is_admin(bot, message.chat.id, message.from_user.id):
            return
        words = get_banned_words(message.chat.id)
        if words:
            bot.reply_to(message, "Запрещенные слова группы:\n" + "\n".join(words))
        else:
            bot.reply_to(message, "Список слов пуст")

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'audio'])
def handle_messages(message):
    if message.chat.type in ['group', 'supergroup']:
        if is_admin(bot, message.chat.id, message.from_user.id):
            return
            
        text_to_check = message.text or message.caption
        if (text_to_check and is_link(text_to_check, message.chat.id)) or contains_telegram_entities(message):
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except telebot.apihelper.ApiTelegramException:
                pass


if __name__ == '__main__':
    bot.infinity_polling()