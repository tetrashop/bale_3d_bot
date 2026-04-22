import os
import logging
from telegram import Update, InputFile
from telegram.ext import (
Updater,
CommandHandler,
MessageHandler,
Filters,
CallbackContext,
)
from worker import add_job
OUTPUT_DIR = "./output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO)
def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! لطفا یک عکس ارسال کنید تا مدل سهبعدی ساخته شود.")
    def handle_photo(update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        photos = update.message.photo
        if not photos:
            update.message.reply_text("تصویری ارسال کنید.")
            return
            photo = photos[-1]
            image_path = os.path.join(OUTPUT_DIR, f"{chat_id}_input.jpg")
            output_path = os.path.join(OUTPUT_DIR, f"{chat_id}_model.3dm")
            photo.get_file().download(custom_path=image_path)
            update.message.reply_text("عکس دریافت شد، مدل سهبعدی در حال ساخته شدن است...")
            def callback(chat_id, model_path):
                if model_path and os.path.exists(model_path):
                    with open(model_path, "rb") as f:
                        context.bot.send_document(
                        chat_id=chat_id, document=InputFile(f, filename="model.3dm")
                        )
                        try:
                            os.remove(image_path)
                            os.remove(model_path)
                        except Exception:
                            pass
                        else:
                            context.bot.send_message(
                            chat_id=chat_id, text="خطایی روی داد، لطفا مجددا تلاش کنید."
                            )
                            add_job(chat_id, image_path, output_path, callback)
                            def main():
                                TOKEN = "659328109:mN9SeG5__szWuwQrDsJK5zOHPDf7ad0uT4E"
                                updater = Updater(TOKEN)
                                dp = updater.dispatcher
                                dp.add_handler(CommandHandler("start", start))
                                dp.add_handler(MessageHandler(Filters.photo, handle_photo))
                                updater.start_polling()
                                updater.idle()
                                if __name__ == "__main__":
                                    main()
