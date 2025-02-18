import asyncio,aiohttp,io
from telebot.async_telebot import AsyncTeleBot
from telebot import *
from kvsqlite.sync import Client
from datetime import datetime
from pdf2image import convert_from_bytes

users = Client('./db/users.sqlite')
req = Client('./db/req.sqlite')
admin = Client('./db/admin.sqlite')

start_msg = open('start_message.txt','r').read()
support_msg = open('support_bot.txt','r').read()

time = datetime.now()
pdf = []

bot = AsyncTeleBot('7404500425:AAHxUetTSf1iBMyyF3XbyqbUoEwpOdaq8J4')

def markup_gen(loop):
    keyboard = types.InlineKeyboardMarkup(row_width=7)
    for _ in loop.items():
        keyboard.add(
                types.InlineKeyboardButton(
                    text=f"{_[0]}",
                    callback_data=f"{_[1]}",
                ))
    return keyboard

def markup_start():
    keyboard = types.InlineKeyboardMarkup(row_width=7)
    keyboard.add(
            types.InlineKeyboardButton(
                text=f"احصائيات البوت",
                callback_data=f"info_bot",
            ))
    keyboard.add(
            types.InlineKeyboardButton(
                text=f"المساهمين",
                callback_data=f"support_bot",
            ))
    keyboard.add(
            types.InlineKeyboardButton(
                text=f"اقتراح - استفسار",
                url=f"tg://user?id=5029420526",
            ))
    return keyboard

def markup_celender():
    keyboard = types.InlineKeyboardMarkup(row_width=7)
    keyboard.add(
        types.InlineKeyboardButton(
            text=f"التقويم الاكاديمي",
            web_app=types.WebAppInfo(f"https://www.arabou.edu.sa/ar/students/pages/academic-calendar.aspx"),
    ))
    keyboard.add(
    types.InlineKeyboardButton(
        text=f"جدول الاختبارات النصفية",
        web_app=types.WebAppInfo(f"https://www.arabou.edu.sa/ar/students/examinations/Pages/MTA-Exam.aspx"),
    ))
    keyboard.add(
    types.InlineKeyboardButton(
        text=f"جدول الاختبارات النهائية",
        web_app=types.WebAppInfo(f"https://www.arabou.edu.sa/ar/students/examinations/Pages/Final-Exam.aspx"),
    ))

    return keyboard

def keyboard_start():
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=7)
        keyboard.add(
            types.KeyboardButton('السلايدات'),
            types.KeyboardButton('الكتب'),
        )
        keyboard.add(
            types.KeyboardButton('المواعيد'),
            types.KeyboardButton('الايميلات'),
        )
        keyboard.add(
            types.KeyboardButton('الاسئلة الشائعه')
        )
        keyboard.add(
            types.KeyboardButton('تحويل ملف pdf الى صور png')
        )
        return keyboard


@bot.message_handler(commands=['start'],content_types=['text'],chat_types=['private'])
async def main_start(message):
    if message.chat.id == 50294205260:
        pass
    elif admin.exists(f'{message.chat.id}'):
        pass
    else:
        if users.exists(f"{message.chat.id}"):
            await bot.send_message(message.chat.id,start_msg,reply_to_message_id=message.message_id,reply_markup=markup_start())
            await bot.send_message(message.chat.id,"- اختر خدمة من الخدمات المتاحه .",reply_markup=keyboard_start())
        else:
            await bot.send_message(message.chat.id,start_msg,reply_to_message_id=message.message_id,reply_markup=markup_start())
            await bot.send_message(message.chat.id,"- اختر خدمة من الخدمات المتاحه .",reply_markup=keyboard_start())
            users.set(f'{message.chat.id}',{'time':f"{time.year}-{time.month}-{time.day}"})



@bot.message_handler(func=lambda message:message.text=='المواعيد' , chat_types=['private'])
async def main_msg3(message):
    await bot.send_message(message.chat.id,'- اختر احد المواعيد .',reply_to_message_id=message.message_id,reply_markup=markup_celender())


@bot.message_handler(func=lambda message:message.text=='تحويل ملف pdf الى صور png' , chat_types=['private'])
async def main_msg6(message):
    if len(pdf)==5:
        await bot.send_message(message.chat.id,'- يرجى المحاوله في وقت لاحق .',reply_to_message_id=message.message_id)
    else:
        await bot.send_message(message.chat.id,'- ارسل ملف pdf ليتم تحويله الى صور .',reply_to_message_id=message.message_id,reply_markup=markup_gen({"الغاء":"cancel"}))
        pdf.append(f"{message.chat.id}")


@bot.message_handler(chat_types=['private'],content_types=['document'])
async def convert_pdf_to_png(message):
    if req.get(f"{message.chat.id}")=='document':
        try:
            if message.document.mime_type == 'application/pdf':
                file_info = await bot.get_file(message.document.file_id)
                file_data = await bot.download_file(file_info.file_path)
                images = convert_from_bytes(file_data,dpi=300,first_page=1,last_page=5)
                for img in images:
                    byte_io = io.BytesIO()
                    img.save(byte_io, 'PNG')
                    byte_io.seek(0)
                    await bot.send_photo(message.chat.id, byte_io)
                    pdf.remove(f"{message.chat.id}")
                    byte_io.close()
        except:
            await bot.reply_to(message,'- لا يمكن تحويل هذا الملف , حاول في وقت لاحق !')
    else:
        pass


@bot.callback_query_handler(func=lambda call:True)
async def call_main(call):
    if call.data == 'info_bot':
        await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=
                            "- احصائيات البوت :\n"
                            f"• عدد مستخدمين البوت : {len(users.keys())}\n"
                            f"• عدد الكتب المنشوره : {"1"}\n"
                            f"• عدد السلايدات المنشوره : {"1"}",
                            reply_markup=markup_gen({"الرجوع":"back"}))
    elif call.data == 'back':
        await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=start_msg,reply_markup=markup_start())


if __name__=="__main__":
    while True:
        try:
            print('Running ...')
            asyncio.run(bot.infinity_polling(skip_pending=True,timeout=1))
        except Exception as e:
            print(f'- Error {e}')