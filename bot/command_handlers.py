from aiogram import Router, html
import asyncio
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command, StateFilter
from python_db import user_dict, users_db, bot_farsi_base
from filters import PRE_START, TICKET_NUMBER_LIST, ZERO_FILTER, IS_DIGIT, IS_TIME, IS_ADMIN
from lexikon import *
from external_functions import get_tickets, get_random_30_questions, scheduler_job, napominalka_sync, return_bally
from copy import deepcopy
from aiogram.fsm.context import FSMContext
from keyboards import pre_start_clava
from aiogram.exceptions import TelegramBadRequest
from postgress_function import *
from FSM import FSM_ST
from tickets import tickets_dict
from bot_instance import scheduler
from contextlib import suppress
from inlinekeyboards import *
from random import randint
import datetime
from datetime import timezone
import pickle

ch_router = Router()


@ch_router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    if not await check_user_in_table(user_id):
        await insert_new_user_in_table(user_id, user_name)
        users_db[message.from_user.id] = deepcopy(user_dict)
        await state.set_state(FSM_ST.after_start)
        await state.set_data({'A': '🔴', 'B': '🟡', 'C': '🟢', 'capture': 0, 'my_tz': 0, 'napomny_time':''})
        await message.answer(text=f'{html.bold(html.quote(user_name))}, '
                                  f'Привет !\n'
                                  f'Я бот для изучения ПДД в Германии. '
                                  f'Для работы со мной нажмите кнопку '
                                  f'<b>Меню</b> \n\n🔹                   /help\n\n'
                                  f'/change_lan  -  اگر به زبان فارسی نیاز دارید کلیک کنید'
                                  f'\n\n🔹                       🚨',
                             parse_mode=ParseMode.HTML,
                             reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(0.5)
    else:
        await state.set_state(FSM_ST.after_start)
        await state.set_data({'A': '🔴', 'B': '🟡', 'C': '🟢', 'capture': 0, 'my_tz': 0, 'napomny_time':''})
        users_db[message.from_user.id] = deepcopy(user_dict)
        await message.answer(text='Бот перезапущен на сервере')
        await message.delete()



@ch_router.message(PRE_START())
async def before_start(message: Message):
    prestart_ant = await message.answer(text='Нажми на кнопку <b>start</b> !',
                                        reply_markup=pre_start_clava)
    await message.delete()
    await asyncio.sleep(8)
    await prestart_ant.delete()



@ch_router.message(Command('help'))
async def help_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    temp_data = users_db[user_id]['temp_msg']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['temp_msg']
            await temp_message.delete()
            users_db[user_id]['temp_msg'] = ''

    lan = users_db[user_id]['lan']
    if lan == 'ru':
        att = await message.answer(help)
    else:
        fa_key = help[:12]
        if fa_key not in bot_farsi_base:
            fa_text = await translates(help, lan)
            bot_farsi_base[fa_key]= fa_text + '/presentation'
            att = await message.answer(f'{fa_text}  /presentation')
        else:
            att = await message.answer(text=bot_farsi_base[fa_key])
    users_db[user_id]['bot_answer'] = att
    await asyncio.sleep(2)
    await message.delete()


@ch_router.message(Command('presentation'), StateFilter(FSM_ST.after_start))
async def presentation_command(message: Message):
    user_id = message.from_user.id
    lan = users_db[user_id]['lan']
    if lan == 'ru':
        await message.answer(text='https://youtu.be/gDee19N3gqI')
    else:
        await message.answer(text='https://youtu.be/wsgv6mNkb04')
    await asyncio.sleep(2)
    await message.delete()


@ch_router.message(Command('change_lan'), StateFilter(FSM_ST.after_start))
async def change_language(message: Message, state: FSMContext):
    user_id = message.from_user.id
    temp_data = users_db[user_id]['temp_msg']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['temp_msg']
            await temp_message.delete()
            users_db[user_id]['temp_msg'] = ''
    lan = users_db[user_id]['lan']
    if lan == 'ru':
        att = await message.answer(text = change_lan, reply_markup=fa_kb)
    else:
        fa_key = change_lan[:10]
        if fa_key not in bot_farsi_base:
            fa_text = await translates(change_lan, lan)
            bot_farsi_base[fa_key] = fa_text
            att = await message.answer(fa_text, reply_markup=rus_kb)
        else:
            att = await message.answer(text=bot_farsi_base[fa_key], reply_markup=rus_kb)
    users_db[user_id]['temp_msg'] = att


@ch_router.message(Command('get_ticket'), StateFilter(FSM_ST.after_start))
async def get_ticket_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    temp_data = users_db[user_id]['temp_msg']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['temp_msg']
            await temp_message.delete()
            users_db[user_id]['temp_msg'] = ''
    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['bot_answer']
            await temp_message.delete()

    await state.set_state(FSM_ST.ganz_ant)

    lan = users_db[user_id]['lan']
    if lan == 'ru':
        att = await message.answer("Введите номер билета или нажмите  <b>Новый Билет</b>",
                                   reply_markup=next_bilet)
    else:
        att = await message.answer(text='شماره بلیط خود را وارد کنید یا روی - New Ticket کلیک کنید', reply_markup=next_bilet_fa)

    users_db[message.from_user.id]['bot_answer'] = att
    await asyncio.sleep(2)
    await message.delete()


@ch_router.message(StateFilter(FSM_ST.ganz_ant), TICKET_NUMBER_LIST(), ZERO_FILTER())
async def list_release(message: Message):
    """Функция загружающая билет по номеру от 1 до 30"""
    print('First Bilet')
    user_id = message.from_user.id
    temp_data = users_db[user_id]['temp_msg']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['temp_msg']
            await temp_message.delete()
            users_db[user_id]['temp_msg'] = ''
    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['bot_answer']
            await temp_message.delete()
    frage_list = get_tickets(int(message.text))  # Получаю массив с 30 вопросами
    print('frage list = ', frage_list)
    await insert_new_ticket(user_id, frage_list)
    key = frage_list[0]  #  Это реальный номер билета
    users_db[user_id]['tik_nummer'] = key  # Это id_tikest
    users_db[user_id]['bilet_number'] = int(message.text)
    await message.answer(f'🔹 <b>{ticket_index}  # {return_bally(message.text)}</b>')  # Билет № 1
    num = 1
    ticket = tickets_dict[key]
    lan = users_db[user_id]['lan']
    if ticket['foto_id']:
        if lan == 'ru':
            await message.answer_photo(photo=ticket['foto_id'], caption=f'<b>#  {num}</b>  {ticket["desc"]}',
                                   reply_markup=None)
        else:
            fa_key = key  # Один из 900 от 1001 до 1900
            if fa_key not in bot_farsi_base:
                fa_text = await translates(ticket["desc"], lan)
                bot_farsi_base[fa_key] = fa_text
                await message.answer_photo(photo=ticket['foto_id'], caption=f'<b>#  {num}</b>  {fa_text}',
                                   reply_markup=None)
            else:
                await message.answer_photo(photo=ticket['foto_id'], caption=f'<b>#  {num}</b>  {bot_farsi_base[fa_key]}',
                                   reply_markup=None)
    elif ticket['text_frage']:
        if lan == 'ru':
            await message.answer(text=f'<b>#  {num}</b>  {ticket["text_frage"]}',
                                 reply_markup=None)
        else:
            fa_key = key
            if fa_key not in bot_farsi_base:
                fa_text = await translates(ticket["text_frage"], lan)
                bot_farsi_base[fa_key] = fa_text
                await message.answer(text=f'<b>#  {num}</b>  {fa_text}',
                                           reply_markup=None)
            else:
                await message.answer(text=f'<b>#  {num}</b>  {bot_farsi_base[fa_key]}',
                                           reply_markup=None)
    else:
        if lan == 'ru':
            await message.answer_video(video=ticket['video_id'], caption=f'<b>#  {num}</b>  {ticket["desc"]}',
                                       reply_markup=None)
        else:
            fa_key = key  # Один из 900 от 1001 до 1900
            if fa_key not in bot_farsi_base:
                fa_text = await translates(ticket["desc"], lan)
                bot_farsi_base[fa_key] = fa_text
                await message.answer_video(video=ticket['video_id'], caption=f'<b>#  {num}</b>  {fa_text}',
                                           reply_markup=None)
            else:
                await message.answer_video(video=ticket['video_id'],
                                           caption=f'<b>#  {num}</b>  {bot_farsi_base[fa_key]}',
                                           reply_markup=None)
    if lan == 'ru':
        att = await message.answer(base_antwort,
                                   reply_markup=abc_kb)
    else:
        att = await message.answer(text=base_antwort_fa,
                             reply_markup=abc_kb)

    users_db[user_id]['bot_answer'] = att


@ch_router.message(Command('get_30_questions'), ZERO_FILTER(), StateFilter(FSM_ST.after_start))
async def get_30_questions_command(message: Message, state: FSMContext):
    await state.set_state(FSM_ST.ganz_ant)
    user_id = message.from_user.id
    temp_data = users_db[user_id]['temp_msg']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['temp_msg']
            await temp_message.delete()
            users_db[user_id]['temp_msg'] = ''
    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['bot_answer']
            await temp_message.delete()
    frage_list = get_random_30_questions()
    print('frage list = ', frage_list)
    await insert_new_ticket(user_id, frage_list)
    key = frage_list[0]
    users_db[user_id]['tik_nummer'] = key

    num = 1
    ticket = tickets_dict[key]
    lan = users_db[user_id]['lan']
    if ticket['foto_id']:
        if lan == 'ru':
            await message.answer_photo(photo=ticket['foto_id'], caption=f'<b>#  {num}</b>  {ticket["desc"]}',
                                       reply_markup=None)
        else:
            fa_key = key  # Один из 900 от 1001 до 1900
            if fa_key not in bot_farsi_base:
                fa_text = await translates(ticket["desc"], lan)
                bot_farsi_base[fa_key] = fa_text
                await message.answer_photo(photo=ticket['foto_id'], caption=f'<b>#  {num}</b>  {fa_text}',
                                           reply_markup=None)
            else:
                await message.answer_photo(photo=ticket['foto_id'],
                                           caption=f'<b>#  {num}</b>  {bot_farsi_base[fa_key]}',
                                           reply_markup=None)
    elif ticket['text_frage']:
        if lan == 'ru':
            await message.answer(text=f'<b>#  {num}</b>  {ticket["text_frage"]}',
                                 reply_markup=None)
        else:
            fa_key = key
            if fa_key not in bot_farsi_base:
                fa_text = await translates(ticket["text_frage"], lan)
                bot_farsi_base[fa_key] = fa_text
                await message.answer(text=f'<b>#  {num}</b>  {fa_text}',
                                     reply_markup=None)
            else:
                await message.answer(text=f'<b>#  {num}</b>  {bot_farsi_base[fa_key]}',
                                     reply_markup=None)
    else:
        if lan == 'ru':
            await message.answer_video(video=ticket['video_id'], caption=f'<b>#  {num}</b>  {ticket["desc"]}',
                                       reply_markup=None)
        else:
            fa_key = key  # Один из 900 от 1001 до 1900
            if fa_key not in bot_farsi_base:
                fa_text = await translates(ticket["desc"], lan)
                bot_farsi_base[fa_key] = fa_text
                await message.answer_video(video=ticket['video_id'], caption=f'<b>#  {num}</b>  {fa_text}',
                                           reply_markup=None)
            else:
                await message.answer_video(video=ticket['video_id'],
                                           caption=f'<b>#  {num}</b>  {bot_farsi_base[fa_key]}',
                                           reply_markup=None)

                ###############################################################
    if lan == 'ru':
        att = await message.answer(base_antwort,
                                   reply_markup=abc_kb)
    else:
        fa_key = base_antwort[:10]
        if fa_key not in bot_farsi_base:
            bot_farsi_base[fa_key] = base_antwort_fa
            att = await message.answer(text=f'<b>#  {num}</b>  {base_antwort_fa}',
                                       reply_markup=abc_kb)
        else:
            att = await message.answer(text=f'<b>#  {num}</b>  {bot_farsi_base[fa_key]}',
                                       reply_markup=abc_kb)

    users_db[user_id]['bot_answer'] = att
    await asyncio.sleep(2)
    await message.delete()


@ch_router.message(Command('exit'))
async def exit_command(message: Message, state: FSMContext):
    us_state = await state.get_state()
    user_id = message.from_user.id
    if us_state == 'FSM_ST:exam':  # FSM_ST:ganz_ant
        stop_exam = 'exam' + str(user_id)
        scheduler.remove_job(stop_exam)
    await state.set_state(FSM_ST.after_start)

    temp_data = users_db[user_id]['temp_msg']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['temp_msg']
            await temp_message.delete()
            users_db[user_id]['temp_msg'] = ''
    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['bot_answer']
            await temp_message.delete()
    users_db[user_id]['bilet_number'] = 0
    await reset_ticket_list(user_id)

    users_db[user_id]['current_tic_number'] = 0
    users_db[user_id]['right_answer'] = 0
    users_db[user_id]['tik_nummer'] = 0
    lan = users_db[user_id]['lan']
    if lan == 'ru':
        att = await message.answer(for_continue)
    else:
        fa_key = for_continue[:10]
        if fa_key not in bot_farsi_base:
            fa_text = await translates(change_lan, lan)
            bot_farsi_base[fa_key] = fa_text
            att = await message.answer(fa_text, reply_markup=None)
        else:
            att = await message.answer(text=bot_farsi_base[fa_key], reply_markup=None)

    users_db[user_id]['bot_answer'] = att
    await asyncio.sleep(2)
    await message.delete()


@ch_router.message(Command('pruefung'), ZERO_FILTER(), StateFilter(FSM_ST.after_start))
async def exam_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lan = users_db[user_id]['lan']
    await state.set_state(FSM_ST.exam)
    scheduler_job(user_id, state)  # Ставлю таймер
    temp_data = users_db[user_id]['temp_msg']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['temp_msg']
            await temp_message.delete()
            users_db[user_id]['temp_msg'] = ''
    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['bot_answer']
            await temp_message.delete()
    if lan == 'ru':
        await message.answer(start_exam)
    else:
        await message.answer(start_exam_fa)
    frage_list = get_random_30_questions()
    print('frage list = ', frage_list)
    await insert_new_ticket(user_id, frage_list)
    key = frage_list[0]
    users_db[user_id]['tik_nummer'] = key
    num = 1
    ticket = tickets_dict[key]
    lan = users_db[user_id]['lan']
    if ticket['foto_id']:
        if lan == 'ru':
            await message.answer_photo(photo=ticket['foto_id'], caption=f'<b>#  {num}</b>  {ticket["desc"]}',
                                       reply_markup=None)
        else:
            fa_key = key  # Один из 900 от 1001 до 1900
            if fa_key not in bot_farsi_base:
                fa_text = await translates(ticket["desc"], lan)
                bot_farsi_base[fa_key] = fa_text
                await message.answer_photo(photo=ticket['foto_id'], caption=f'<b>#  {num}</b>  {fa_text}',
                                           reply_markup=None)
            else:
                await message.answer_photo(photo=ticket['foto_id'],
                                           caption=f'<b>#  {num}</b>  {bot_farsi_base[fa_key]}',
                                           reply_markup=None)
    elif ticket['text_frage']:
        if lan == 'ru':
            await message.answer(text=f'<b>#  {num}</b>  {ticket["text_frage"]}',
                                 reply_markup=None)
        else:
            fa_key = key
            if fa_key not in bot_farsi_base:
                fa_text = await translates(ticket["text_frage"], lan)
                bot_farsi_base[fa_key] = fa_text
                await message.answer(text=f'<b>#  {num}</b>  {fa_text}',
                                     reply_markup=None)
            else:
                await message.answer(text=f'<b>#  {num}</b>  {bot_farsi_base[fa_key]}',
                                     reply_markup=None)
    else:
        if lan == 'ru':
            await message.answer_video(video=ticket['video_id'], caption=f'<b>#  {num}</b>  {ticket["desc"]}',
                                       reply_markup=None)
        else:
            fa_key = key  # Один из 900 от 1001 до 1900
            if fa_key not in bot_farsi_base:
                fa_text = await translates(ticket["desc"], lan)
                bot_farsi_base[fa_key] = fa_text
                await message.answer_video(video=ticket['video_id'], caption=f'<b>#  {num}</b>  {fa_text}',
                                           reply_markup=None)
            else:
                await message.answer_video(video=ticket['video_id'],
                                           caption=f'<b>#  {num}</b>  {bot_farsi_base[fa_key]}',
                                           reply_markup=None)
    if lan == 'ru':
        att = await message.answer(base_antwort,
                                   reply_markup=abc_kb)
    else:
        fa_key = base_antwort[:10]
        if fa_key not in bot_farsi_base:
            bot_farsi_base[fa_key] = base_antwort_fa
            att = await message.answer(text=f'<b>#  {num}</b>  {base_antwort_fa}',
                                       reply_markup=abc_kb)
        else:
            att = await message.answer(text=f'<b>#  {num}</b>  {bot_farsi_base[fa_key]}',
                                       reply_markup=abc_kb)

    users_db[user_id]['bot_answer'] = att
    await asyncio.sleep(2)
    await message.delete()


@ch_router.message(Command('settings'), StateFilter(FSM_ST.after_start))
async def settings_command(message: Message):
    user_id = message.from_user.id
    lan = users_db[user_id]['lan']
    if lan == 'ru':
        att = await message.answer(text=settings, reply_markup=None)
    else:
        fa_key = settings[:10]
        if fa_key not in bot_farsi_base:
            fa_text = await translates(settings, lan)
            bot_farsi_base[fa_key] = fa_text
            att = await message.answer(fa_text, reply_markup=None)
        else:
            att = await message.answer(text=bot_farsi_base[fa_key], reply_markup=None)
    await asyncio.sleep(2)
    await message.delete()


@ch_router.message(Command('timer'), StateFilter(FSM_ST.after_start))
async def timer_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    us_dict = await state.get_data()
    napomny_time = us_dict['napomny_time']
    lan = users_db[user_id]['lan']
    if lan == 'ru':
        if napomny_time:
            await message.answer(f'{allready_exists} <b>{napomny_time}</b>')
        else:
            await state.set_state(FSM_ST.settings)
            first_num = 1
            second_num = randint(1, 9)
            summa = first_num + second_num
            await state.update_data(capture=summa)
            temp_data = users_db[user_id]['bot_answer']
            if temp_data:
                with suppress(TelegramBadRequest):
                    temp_message = users_db[user_id]['bot_answer']
                    await temp_message.delete()
            att = await message.answer(f'{timer}<b>{first_num} + {second_num}  =  ?</b>')
            await asyncio.sleep(2)
            await message.delete()
            users_db[message.from_user.id]['bot_answer'] = att
    else:
        await message.answer(text=unavailable)


@ch_router.message(StateFilter(FSM_ST.settings), IS_DIGIT())
async def validate_capture(message: Message, state: FSMContext):
    user_id = message.from_user.id
    us_dict = await state.get_data()
    secret_sum = us_dict['capture']
    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['bot_answer']
            await temp_message.delete()
    lan = users_db[user_id]['lan']
    if lan == 'ru':
        if secret_sum == int(message.text):
            timezone_offset = 2.0  # время бота
            tz_bot = timezone(datetime.timedelta(hours=timezone_offset))
            time_now = datetime.datetime.now(tz_bot)
            # time_now = datetime.datetime.now()
            format_time = '%H:%M'
            print(time_now.strftime(format_time))
            att = await message.answer(f'{wie_viel_uhr}  <b>{time_now.strftime(format_time)}</b>\n\n'
                                       f'А у Вас сколько ?', reply_markup=tz_kb)
            users_db[message.from_user.id]['bot_answer'] = att

        else:
            att = await message.answer(hvatit)
            await state.set_state(FSM_ST.after_start)
            users_db[message.from_user.id]['bot_answer'] = att
    else:
        await message.answer(unavailable)
    await asyncio.sleep(2)
    await message.delete()


@ch_router.message(IS_TIME(), StateFilter(FSM_ST.settings))
async def validate_time(message: Message, state: FSMContext):
    '''Функция принимает строку вида 12:17'''
    user_id = message.from_user.id
    # jetzt = datetime.datetime.now()  # 2024-08-23 14:44:02.083133

    timezone_offset = 2.0  # время бота
    tz_bot = timezone(datetime.timedelta(hours=timezone_offset))
    datetime.datetime.now(tz_bot)

    # jetzt = datetime.datetime.now(tz_bot)

    # print('jetzt = ', jetzt)  # 2024-08-26 22:50:21.402277+02:00
    # data = str(datetime.datetime.astimezone(jetzt))
    # #  Нам нужна только цифра 2 в конце строки. Код ниже это делает
    # print('data = ', data)  # data =  2024-08-26 20:50:21.402277+00:00
    # nedeed_data = data.split('+')[1]  # 00:00
    # ohne_null = int(nedeed_data.split(':')[0]) # 0
    us_dict = await state.get_data() #
    tz_sdvig = us_dict['my_tz'] #
    offset = datetime.timedelta(hours= tz_sdvig)  #ohne_null + tz_sdvig)

    tz = datetime.timezone(offset)  # в timezone нужно передавать timedelta
    await state.update_data(napomny_time=message.text)
    napominalka_sync(user_id, message.text, tz)  # Запускаю планировщик
    await message.answer(f'{set_napom}  <b>{message.text}</b>') # \n\n jetzt = {jetzt}')
    await state.set_state(FSM_ST.after_start)


@ch_router.message(Command('delete_schedule'))
async def delete_schedule_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lan = users_db[user_id]['lan']
    if lan == 'ru':
        try:
            scheduler.remove_job(str(user_id))
            await message.answer('График оповещений отменён')
            await state.update_data(napomny_time='')
        except Exception:  # JobLookupError:
            await message.answer('У Вас нет графика напоминаний')
        await state.set_state(FSM_ST.after_start)
    else:
        await message.answer(unavailable)
    await asyncio.sleep(2)
    await message.delete()


@ch_router.message(Command('stat'))
async def get_my_right_answers(message: Message):
    user_id = message.from_user.id
    right = await return_total(user_id)
    lan = users_db[user_id]['lan']
    if lan == 'ru':
        await message.answer(f'Количество правильно отвеченных вопросов   <b>{right}</b>')
    else:
        await message.answer(f'{right_ans}   <b>{right}</b>')


#####################################ADMIN##############################################

@ch_router.message(Command('admin'), IS_ADMIN())
async def admin_enter(message: Message):
    print('admin_enter works')
    att = await message.answer(admin_eintritt)
    await asyncio.sleep(12)
    await att.delete()


@ch_router.message(Command('skolko'), IS_ADMIN())
async def get_quantyty_users(message: Message):
    qu = await get_user_count()
    str_qu = str(qu)
    last_number = str_qu[-1]
    if last_number in ('2', '3', '4'):
        await message.answer(f'Бота запустили <b>{qu}</b> юзера')
    elif last_number == '1':
        await message.answer(f'Бота запустили <b>{qu}</b> юзер')
    else:
        await message.answer(f'Бота запустили <b>{qu}</b> юзеров')


@ch_router.message(IS_ADMIN(), Command('dump'))
async def dump_db(message: Message, state: FSMContext):
    with open('save_db.pkl', 'wb') as file:
        pickle.dump(bot_farsi_base, file)

    await message.answer('Базы данных успешно записана !')
    await state.set_state(FSM_ST.after_start)

@ch_router.message(IS_ADMIN(), Command('load'))
async def load_db(message: Message, state: FSMContext):
    with open('save_db.pkl', 'rb') as file:
        recover_base = pickle.load(file)
        bot_farsi_base.update(recover_base)
    await message.answer('База данных успешно загружена !')
    await state.set_state(FSM_ST.after_start)


@ch_router.message()
async def trasher(message: Message):
    print(f'TRASHER DELETE DATA  FROM USER {message.from_user.first_name}  ID {message.from_user.id}')
    await asyncio.sleep(1)
    await message.delete()
