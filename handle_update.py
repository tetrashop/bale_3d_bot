def handle_update(update, bot):
    message = update.get("message")
    if not message:
        return
        chat_id = message.get("chat", {}).get("id")
        if not chat_id:
            return
            text = message.get("text", "").strip() if "text" in message else ""
            try:
                # دستورات شناخته شده
                if text in ["/start", "/help"]:
                    send_main_menu(bot, chat_id)
                    return
                    # دستور خرید اعتبار (نمونه)
                    if text.startswith("/buy"):
                        # اینجا کد خرید اعتبار مثلا بر اساس متن
                        # مثال:
                            if text == "/buy1":
                                bot.send_invoice(chat_id, PRICES["1_credit"], "یک تبدیل")
                                bot.send_message(chat_id, "درگاه پرداخت یک تبدیل ارسال شد.")
                                return
                            elif text == "/buy10":
                                bot.send_invoice(chat_id, PRICES["10_credits"], "ده تبدیل")
                                bot.send_message(chat_id, "درگاه پرداخت بسته ده تایی ارسال شد.")
                                return
                            else:
                                bot.send_message(chat_id, "دستور خرید نامشخص است.")
                                return
                                # سایر فرمانهای اصلی اینجا بررسی شوند...
                                # اگر پیام عکس یا فایل تصویری بود:
                                    if "photo" in message or ("document" in message and message["document"].get("mime_type", "").startswith("image")):
                                        # کد پردازش عکس و تبدیل به مدل سهبعدی (مشابه سابق)
                                        # ...
                                        return
                                        # سایر حالات متنی یا عملیاتها...
                                        # **لحظه catch-all: ورودی نامعتبر یا ناشناخته**
                                        send_main_menu(bot, chat_id)
                                        logger.warning(f"Unknown command from {chat_id}: '{text}'")
                                    except Exception as e:
                                        logger.error(f"Error in handle_update for chat {chat_id}: {e}", exc_info=True)
                                        bot.send_message(chat_id, "خطایی رخ داد، لطفا دوباره تلاش کنید.")
