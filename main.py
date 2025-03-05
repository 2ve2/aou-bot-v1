import asyncio,aiohttp,io,json
from telebot.async_telebot import AsyncTeleBot
from telebot import *
from kvsqlite.sync import Client
from datetime import datetime
# from pdf2image import convert_from_bytes

users = Client('./db/users.sqlite')
admin = Client('./db/admin.sqlite')
req = Client('./db/req.sqlite')
req2 = Client('./db/req2.sqlite')


time = datetime.now()
OWNER = 5029420526

bot = AsyncTeleBot('7404500425:AAHxUetTSf1iBMyyF3XbyqbUoEwpOdaq8J4')

# markup generate
def markup_gen(loop):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for _ in loop.items():
        keyboard.add(
                types.InlineKeyboardButton(
                    text=f"{_[0]}",
                    callback_data=f"{_[1]}",
                ))
    return keyboard

# markup start
def markup_start(chat_id):
    keyboard = types.InlineKeyboardMarkup(row_width=7)
    keyboard.add(
            types.InlineKeyboardButton(
                text=f"قناة البوت",
                url=f"https://t.me/aouksaa",
            ),        
            types.InlineKeyboardButton(
            text=f"شارك البوت",
            url="Https://t.me/share?url=t.me/aouksabot"
        ))
    keyboard.add(
            types.InlineKeyboardButton(
                text=f"اقتراح - استفسار",
                url=f"tg://user?id=5029420526",
            ))
    if admin.exists(f"{chat_id}") or OWNER == chat_id:
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"الاعدادات",
                callback_data=f"settings",
            ))
        return keyboard
    else:
        if users.exists(f"{chat_id}"):
            return keyboard
        else:
            users.set(f'{chat_id}',{'time':f"{time.year}-{time.month}-{time.day}"})
            return keyboard

# markup celendar
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

# keyboaord start
def keyboard_start():
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            types.KeyboardButton('السلايدات'),
            types.KeyboardButton('الكتب'),
        )
        keyboard.add(
            types.KeyboardButton('المواعيد'),
            types.KeyboardButton('الايميلات'),
        )
        keyboard.add(
            types.KeyboardButton('الخطط الدراسية لجميع التخصصات')
        )
        keyboard.add(
            types.KeyboardButton('الاسئلة الشائعه')
        )
        return keyboard

# keyboard generate
def keyboard_gen(loop):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(loop), 2):
        keyboard.add(
            types.KeyboardButton(loop[i]),
            types.KeyboardButton(loop[i+1]),
        )
    keyboard.add(
            types.KeyboardButton('الرجوع')
        )
    return keyboard


# keyboard generate
def keyboard_gen1(loop):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in loop:
        keyboard.add(
            types.KeyboardButton(i),
        )
    keyboard.add(
            types.KeyboardButton('الرجوع')
        )
    return keyboard

# function to add books and slides
def add_books_or_slides(title,file_id,value,name):
    with open('./other/info.json', 'r+', encoding='utf-8') as file:
        data = json.load(file)
        info = {
            'title': f'{title}',
            value: f'{file_id}',
        }
        data[f'{name}'].append(info)
        file.seek(0)
        json.dump(data, file, indent=4, ensure_ascii=False)
    return True

# function to get info books , slides , etc
def get_info_aou():
        with open('./other/info.json', 'r', encoding='utf-8') as file:
            return json.load(file)

# function get info from data.json
def get_info_emails():
    with open('./other/data.json', 'r', encoding='utf-8') as file:
        return json.load(file)


# start message
@bot.message_handler(commands=['start'],content_types=['text'],chat_types=['private'])
async def main_start(message):
    await bot.send_message(message.chat.id,''.join(get_info_aou()['start_msg']),reply_to_message_id=message.message_id,reply_markup=markup_start(message.chat.id))
    await bot.send_message(message.chat.id,"- اختر خدمة من الخدمات المتاحه .",reply_markup=keyboard_start())

# add admin
@bot.message_handler(commands=['add'],chat_types=['private'])
async def add_admin(message):
    if message.chat.id == OWNER:
        admin.set(f"{message.text.split("/add ")[1]}",True)
        await bot.reply_to(message,'- تم اضافته الى قائمة الادمنيه .')

# delete admin
@bot.message_handler(commands=['delete'],chat_types=['private'])
async def delete_admin(message):
    if message.chat.id == OWNER:
        admin.delete(f"{message.text.split("/delete ")[1]}")
        await bot.reply_to(message,'- تم حذفه من قائمة الادمنيه .')

# get books and slides 
@bot.message_handler(func=lambda message:message.text in ["الكتب","السلايدات"])
async def get_books_and_slides(message):
    if message.text == "الكتب":
        req.set(f"{message.chat.id}",{'type':'book'})
        await bot.send_message(message.chat.id,'- ارسل اسم الكتاب .',reply_to_message_id=message.message_id,reply_markup=markup_gen({'الغاء':'cancel'}))
    else:
        req.set(f"{message.chat.id}",{'type':'slide'})
        await bot.send_message(message.chat.id,'- ارسل اسم السلايد .',reply_to_message_id=message.message_id,reply_markup=markup_gen({'الغاء':'cancel'}))


@bot.message_handler(func=lambda message:check_if_in_data(message),chat_types=['private'],content_types=['text','document'])
async def get_info_books_and_slides(message):
    try:
        if req.get(f"{message.chat.id}")['type']=='book':
            try:
                for i in get_info_aou()['books']:
                    if i['title'] == message.text.lower():
                        await bot.send_document(message.chat.id,i['file_id'],message.message_id)
                        req.delete(f"{message.chat.id}")
                if req.get(f"{message.chat.id}")["type"]=='book':
                    await bot.send_message(message.chat.id,'- هذا الكتاب غير متوفر .',reply_to_message_id=message.message_id)
                    req.delete(f"{message.chat.id}")
                else:
                    req.delete(f"{message.chat.id}")
            except:
                req.delete(f"{message.chat.id}")

        elif req.get(f"{message.chat.id}")['type']=='slide':
            try:
                for i in get_info_aou()['slides']:
                    if i['title'] == message.text.lower():
                        await bot.send_document(message.chat.id,i['file_id'],message.message_id)
                        req.delete(f"{message.chat.id}")
                if req.get(f"{message.chat.id}")["type"]=='slide':
                    await bot.send_message(message.chat.id,'- هذا السلايد غير متوفر .',reply_to_message_id=message.message_id)
                    req.delete(f"{message.chat.id}")
                else:
                    req.delete(f"{message.chat.id}")
            except:
                req.delete(f"{message.chat.id}")

        elif req.get(f"{message.chat.id}")['type']=='add_book':
            try:
                if "name" in req.get(f"{message.chat.id}"):
                    title = req.get(f"{message.chat.id}")['name']
                    file_id = message.document.file_id
                    if add_books_or_slides(title=title.lower(),file_id=file_id,value='file_id',name='books'):
                        await bot.send_message(message.chat.id,'- تم اضافة الكتاب .',reply_to_message_id=message.message_id)
                        req.delete(f"{message.chat.id}")
                    else:
                        await bot.send_message(message.chat.id,'- تعذر اضافة هذا الكتاب !!',reply_to_message_id=message.message_id)
                        req.delete(f"{message.chat.id}")
                else:
                    t = req.get(f"{message.chat.id}")
                    t.update({'name':f"{message.text}"})
                    req.set(f"{message.chat.id}",t)
                    await bot.send_message(message.chat.id,"- ارسل ملف الكتاب .",reply_to_message_id=message.message_id,reply_markup=markup_gen({"الغاء":"cancel"}))
            except:
                await bot.send_message(message.chat.id,'- حدث خطأ !!',reply_to_message_id=message.message_id)
                req.delete(f"{message.chat.id}")
        elif req.get(f"{message.chat.id}")['type']=='add_slide':
            try:
                if "name" in req.get(f"{message.chat.id}"):
                    title = req.get(f"{message.chat.id}")['name']
                    file_id = message.document.file_id
                    if add_books_or_slides(title=title.lower(),file_id=file_id,value='file_id',name='slides'):
                        await bot.send_message(message.chat.id,'- تم اضافة السلايد .',reply_to_message_id=message.message_id)
                        req.delete(f"{message.chat.id}")
                    else:
                        await bot.send_message(message.chat.id,'- تعذر اضافة هذا السلايد !!',reply_to_message_id=message.message_id)
                        req.delete(f"{message.chat.id}")
                else:
                    t = req.get(f"{message.chat.id}")
                    t.update({'name':f"{message.text}"})
                    req.set(f"{message.chat.id}",t)
                    await bot.send_message(message.chat.id,"- ارسل ملف السلايد .",reply_to_message_id=message.message_id,reply_markup=markup_gen({"الغاء":"cancel"}))
            except:
                await bot.send_message(message.chat.id,'- حدث خطأ !!',reply_to_message_id=message.message_id)
                req.delete(f"{message.chat.id}")
        elif req.get(f"{message.chat.id}")['type']=='add_qus':
            try:
                if "name" in req.get(f"{message.chat.id}"):
                    if message.text:
                        title = req.get(f"{message.chat.id}")['name']
                        file_id = message.text
                        if add_books_or_slides(title=title.lower(),file_id=file_id,value='answer',name='questions'):
                            await bot.send_message(message.chat.id,'- تم اضافة الاجابه .',reply_to_message_id=message.message_id)
                            req.delete(f"{message.chat.id}")
                        else:
                            await bot.send_message(message.chat.id,'- تعذر اضافة هذه الاجابه !!',reply_to_message_id=message.message_id)
                            req.delete(f"{message.chat.id}")
                    else:
                        title = req.get(f"{message.chat.id}")['name']
                        file_id = message.document.file_id
                        if add_books_or_slides(title=title.lower(),file_id=file_id,value='file_id',name='questions'):
                            await bot.send_message(message.chat.id,'- تم اضافة الاجابه .',reply_to_message_id=message.message_id)
                            req.delete(f"{message.chat.id}")
                        else:
                            await bot.send_message(message.chat.id,'- تعذر اضافة هذه الاجابه !!',reply_to_message_id=message.message_id)
                            req.delete(f"{message.chat.id}")
                else:
                    t = req.get(f"{message.chat.id}")
                    t.update({'name':f"{message.text}"})
                    req.set(f"{message.chat.id}",t)
                    await bot.send_message(message.chat.id,"- ارسل اجابة السؤال .",reply_to_message_id=message.message_id,reply_markup=markup_gen({"الغاء":"cancel"}))
            except:
                await bot.send_message(message.chat.id,'- حدث خطأ !!',reply_to_message_id=message.message_id)
                req.delete(f"{message.chat.id}")   
    except:
        pass
def check_if_in_data(meesage):
    if req.exists(f"{meesage.chat.id}"):
        return True

# get info celendar
@bot.message_handler(func=lambda message:message.text=='المواعيد' , chat_types=['private'])
async def main_get_info_celendar(message):
    await bot.send_message(message.chat.id,'- اختر احد المواعيد .',reply_to_message_id=message.message_id,reply_markup=markup_celender())


# get info branches from json
@bot.message_handler(func=lambda message:message.text == "الايميلات",chat_types=['private'])
async def main_get_info_emails(message):
    await bot.send_message(message.chat.id,"- اختر احد الفروع .",reply_to_message_id=message.message_id,reply_markup=keyboard_gen([branch['branch_name'] for branch in get_info_emails()['branches']]))


# get info department_name from json
@bot.message_handler(func=lambda message:message.text in [branch['branch_name'] for branch in get_info_emails()['branches']],chat_types=['private'])
async def call_get_info_emails(message):
    req2.set(f"{message.chat.id}",{'branch':f"{message.text}"})
    await bot.send_message(message.chat.id,"- اختر احد الاقسام .",reply_to_message_id=message.message_id,reply_markup=keyboard_gen(next([department['department_name'] for department in branch['departments']] for branch in get_info_emails()['branches'] if branch['branch_name'] == message.text)))


# get info emails from json
@bot.message_handler(func=lambda message:message.text in [dept["department_name"] for dept in get_info_emails()["branches"][0]["departments"]],chat_types=['private'])
async def call2_get_info_emails(message):
    try:
        messages = f""
        for branch in get_info_emails()["branches"]:
            if branch["branch_name"] == req2.get(f"{message.chat.id}")['branch']:
                messages+=f"📌 الجامعة العربية المفتوحة - فرع {branch['branch_name']}\n"
                for department in branch["departments"]:
                    if department["department_name"] == str(message.text):
                        messages+=f"🏢 قسم {department['department_name']}\n\n"
                        for email in department["emails"]:
                            messages += f"• 👤 الموظف/ة : {email['name']}\n"
                            messages += f"• ✉️ الايميل : {email['email']}\n-\n"
        await bot.send_message(message.chat.id, messages,reply_to_message_id=message.message_id)
    except:
        pass

# get info plan aou with keyboard
@bot.message_handler(func=lambda message:message.text=='الخطط الدراسية لجميع التخصصات',chat_types=['private'])
async def main_plan_aou(message):
    await bot.send_message(message.chat.id,'- اختر احد الخطط الدراسية .',reply_to_message_id=message.message_id,reply_markup=keyboard_gen([item['title'] for item in get_info_aou()['plan']]))

# get info questions aou with keyboard
@bot.message_handler(func=lambda message:message.text=='الاسئلة الشائعه',chat_types=['private'])
async def main_questions_aou(message):
    await bot.send_message(message.chat.id,'- اختر احد الاسئلة الشائعة .',reply_to_message_id=message.message_id,reply_markup=keyboard_gen1([item['title'] for item in get_info_aou()['questions']]))

# get info questions aou with message
@bot.message_handler(func=lambda message:message.text in [item['title'] for item in get_info_aou()['questions']],chat_types=['private'])
async def call_questions_aou(message):
    try:
        values = [item.get("file_id") or item.get("answer") for item in get_info_aou()["questions"] if item.get("title") == message.text][0]
        print(values)
        if values.startswith("BQA"):
            await bot.send_document(message.chat.id,values,message.message_id)
        else:
            await bot.send_message(message.chat.id,f"{values}",reply_to_message_id=message.message_id)
    except:
        pass     

# get info plan aou with message
@bot.message_handler(func=lambda message:message.text in [item['title'] for item in get_info_aou()['plan']],chat_types=['private'])
async def call_plan_aou(message):
    await bot.send_document(message.chat.id,next(item for item in get_info_aou()['plan'] if item['title'] == message.text)['file_id'],message.message_id)
# # convert pdf to png main
# @bot.message_handler(func=lambda message:message.text=='تحويل ملف pdf الى صور png' , chat_types=['private'])
# async def main_pdf_to_png(message):
#     await bot.send_message(message.chat.id,'- ارسل ملف pdf ليتم تحويله الى صور .',reply_to_message_id=message.message_id,reply_markup=markup_gen({"الغاء":"cancel"}))
#     pdf.set(f"{message.chat.id}",True)

# convert pdf to png script
# @bot.message_handler(chat_types=['private'],content_types=['document'],func=lambda message:pdf.get(f"{message.chat.id}"))
# async def convert_pdf_to_png(message):
#     try:
#         if message.document.mime_type == 'application/pdf':
#             if message.document.file_size > 6000000:
#                 await bot.reply_to(message,'- حجم الملف كبير !')
#                 pdf.delete(f"{message.chat.id}")
#             else:
#                 file_info = await bot.get_file(message.document.file_id)
#                 file_data = await bot.download_file(file_info.file_path)
#                 images = convert_from_bytes(file_data,dpi=300)
#                 for img in images:
#                     byte_io = io.BytesIO()
#                     img.save(byte_io, 'PNG')
#                     byte_io.seek(0)
#                     await bot.send_photo(message.chat.id, byte_io)
#                 await bot.reply_to(message,'- تم الانتهاء .')
#                 pdf.delete(f"{message.chat.id}")
#                 byte_io.close()
#     except:
#         pdf.delete(f"{message.chat.id}")
#         await bot.reply_to(message,'- لا يمكن تحويل هذا الملف , حاول في وقت لاحق !')

# handler = back to menu keyboord
@bot.message_handler(func=lambda message:message.text=='الرجوع',chat_types=['private'])
async def keyboard_back(message):
    await bot.send_message(message.chat.id,"- اختر خدمة من الخدمات المتاحه .",reply_to_message_id=message.message_id,reply_markup=keyboard_start())

# callback = cancel and delete req , pdf data
@bot.callback_query_handler(func=lambda call:call.data=='cancel')
async def call_cancel(call):
    await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="- تم الغاء العمليه .")
    req.delete(f"{call.message.chat.id}")
    req2.delete(f"{call.message.chat.id}")

# callback = back start
@bot.callback_query_handler(func=lambda call:call.data=='back')
async def call_back(call):
    await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text=''.join(get_info_aou()['start_msg']),reply_markup=markup_start(call.message.chat.id))


@bot.callback_query_handler(func=lambda call:call.data=='settings')
async def call_settings(call):
    await bot.send_message(call.message.chat.id,'- اختر احد الاعدادات المتاحه .',reply_markup=markup_gen({"اضافة كتاب":"add_book","اضافة سلايد":"add_slide","اضافة سؤال":"add_qus"}))

@bot.callback_query_handler(func=lambda call:call.data=='add_book')
async def call_add_books(call):
    req.set(f"{call.message.chat.id}",{'type':"add_book"})
    await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="- ارسل اسم الكتاب .",reply_markup=markup_gen({"الغاء":"cancel"}))


@bot.callback_query_handler(func=lambda call:call.data=='add_slide')
async def call_add_slides(call):
    req.set(f"{call.message.chat.id}",{'type':"add_slide"})
    await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="- ارسل اسم السلايد .",reply_markup=markup_gen({"الغاء":"cancel"}))

@bot.callback_query_handler(func=lambda call:call.data=='add_qus')
async def call_add_qus(call):
    req.set(f"{call.message.chat.id}",{'type':"add_qus"})
    await bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="- ارسل عنوان السؤال .",reply_markup=markup_gen({"الغاء":"cancel"}))



if __name__=="__main__":
    while True:
        try:
            print('Running ...')
            asyncio.run(bot.polling(True))
        except Exception as e:
            print(f'- Error {e}')