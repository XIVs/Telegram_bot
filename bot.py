# bot.py
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler
import os
from config import TELEGRAM_TOKEN
from utils.visualize import process_audio_to_video

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Отправь мне аудио или голосовое сообщение — я создам видео-кружок с винилом 🎵")

def handle_audio(update: Update, context: CallbackContext):
    file = update.message.voice or update.message.audio or update.message.document

    if not file:
        update.message.reply_text("Не смог распознать сообщение. Пришли аудиофайл или голосовое сообщение.")
        return

    if update.message.document and not update.message.document.mime_type.startswith("audio/"):
        update.message.reply_text("Пожалуйста, отправьте аудиофайл (MP3, WAV, M4A и т.д.).")
        return

    file_id = file.file_id
    new_file = context.bot.get_file(file_id)
    input_path = f"temp_{file_id}.ogg"
    new_file.download(input_path)

    output_path = process_audio_to_video(input_path)

    if output_path:
        with open(output_path, 'rb') as video:
            context.bot.send_video_note(chat_id=update.message.chat_id, video_note=video)
        os.remove(output_path)
    else:
        update.message.reply_text("Произошла ошибка при обработке аудио.")

    os.remove(input_path)

def main():
    from telegram.ext import Updater  # импорт здесь помогает иногда IDE

    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher  # явно именуем dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.voice | Filters.audio | Filters.document, handle_audio))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
