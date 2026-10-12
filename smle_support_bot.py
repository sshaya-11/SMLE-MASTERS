"""
SMLE Masters — Telegram Customer Service Bot
Powered by Claude AI
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import anthropic

# ── CONFIG — replace with your actual keys ──────────────────
BOT_TOKEN = "8959961648:AAHzJe1Flz9nELrdl2QqfTfewksOh6AsUOg"
ANTHROPIC_API_KEY = "YOUR_NEW_API_KEY_HERE"   # ← ضع الـ Key الجديد هنا
OWNER_CHAT_ID = "YOUR_NUMERIC_TELEGRAM_ID"    # ← رقم فقط من @userinfobot مثل: 123456789
# ────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = """أنت مساعد خدمة عملاء لمنصة SMLE Masters لتحضير اختبار الترخيص الطبي السعودي.

معلومات المنصة:
- البنك يحتوي على أكثر من 4000 سؤال محلول من اختبارات SMLE 2025 والنصف الأول من 2026
- التخصصات: الجراحة العامة، الباطنية، النساء والتوليد، طب الأطفال، الأخلاقيات
- السعر: 206 ريال
- التسليم: ملف رقمي عبر سلة + قناة تيليغرام خاصة
- التفعيل: خلال 24 ساعة من الشراء
- الشارحون: حصلوا على 100 في تخصصاتهم
- متوسط درجات عملائنا: 94+
- قناة تيليغرام: https://t.me/+K6ULjUQNas0zYmZk
- للشراء: salla.sa/smle1masters

قواعد الرد:
- رد باللغة العربية دائماً
- كن ودوداً ومحترفاً
- إذا سألك عن رقم طلب أو مشكلة تقنية لا تعرف حلها، قل: "سأحول سؤالك للفريق وسيتواصل معك قريباً"
- لا تختلق معلومات غير موجودة أعلاه
- ردودك قصيرة وواضحة"""

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك في SMLE Masters! 👋\n\n"
        "كيف يمكنني مساعدتك؟\n"
        "يمكنك سؤالي عن البنك، التفعيل، أو أي استفسار آخر."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_name = update.effective_user.first_name or "طالب"
    
    await update.message.chat.send_action("typing")
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"{user_name}: {user_message}"}
            ]
        )
        
        reply = response.content[0].text
        await update.message.reply_text(reply)
        
        # لو قال "سأحول سؤالك" ← ينبه المالك
        if "سأحول" in reply or "الفريق" in reply:
            if OWNER_CHAT_ID:
                await context.bot.send_message(
                    chat_id=OWNER_CHAT_ID,
                    text=f"⚠️ سؤال يحتاج متابعة من {user_name}:\n\n{user_message}"
                )
    
    except Exception as e:
        await update.message.reply_text(
            "عذراً، حدث خطأ مؤقت. يرجى المحاولة مرة أخرى أو التواصل معنا مباشرة."
        )
        logging.error(f"Error: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logging.info("SMLE Masters Support Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
