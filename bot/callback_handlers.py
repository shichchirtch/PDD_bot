from aiogram import Router
from filters import *
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from python_db import users_db
from aiogram.exceptions import TelegramBadRequest
from lexikon import *
from aiogram.fsm.context import FSMContext
from FSM import FSM_ST
from inlinekeyboards import *
from contextlib import suppress
from tickets import tickets_dict
from external_functions import get_tickets
from bot_instance import scheduler
from postgress_function import *


cb_router = Router()

@cb_router.callback_query(StateFilter(FSM_ST.ganz_ant, FSM_ST.exam), NEXT_FILTER())
async def get_next_question_in_bilet_list(callback: CallbackQuery):
    print('get_next_question in LIST works')
    user_id = callback.from_user.id
    users_db[user_id]['current_tic_number'] += 1   # Увеличиваю индекс
    index_in_list = users_db[user_id]['current_tic_number']
    num = index_in_list + 1  # А это увеличаваю номер билета, он на 1 больше индекса
    current_list = await return_ticket_list(user_id)
    print('index_in_list = ', index_in_list)
    key = current_list[index_in_list] # Получаю уникальный номер вопроса
    print('key = ', key)

    users_db[user_id]['tik_nummer'] = key
    ticket = tickets_dict[key]
    if ticket['foto_id']:
        await callback.message.answer_photo(photo=ticket['foto_id'], caption=f'<b>#  {num}</b>  {ticket["desc"]}',
                                   reply_markup=None)
    elif ticket['text_frage']:
        await callback.message.answer(text=f'<b>#  {num}</b>  {ticket["text_frage"]}',
                             reply_markup=None)
    else:
        await callback.message.answer_video(video=ticket['video_id'], caption=f'<b>#  {num}</b>  {ticket["desc"]}',
                                   reply_markup=None)

    att = await callback.message.answer(base_antwort,
                         reply_markup=abc_kb)

    temp_text = users_db[user_id]['user_ans']  # Это текст юзера
    try:
        await callback.message.edit_text(
            text=temp_text)
    except TelegramBadRequest:
        print("INTO EXCEPTION ")
        await callback.message.edit_text(
            text=temp_text, reply_markup=None)

    users_db[user_id]['bot_answer'] = att
    await callback.answer()


@cb_router.callback_query(StateFilter(FSM_ST.ganz_ant, FSM_ST.exam), ABC_FILTER())
async def button_ABC_press_in_list(callback: CallbackQuery, state:FSMContext):
    user_id = callback.from_user.id
    if callback.data=='🔴':
        await state.update_data(A='')
    if callback.data=='🟡':
        await state.update_data(B='')
    if callback.data=='🟢':
        await state.update_data(C='')
    users_db[user_id]['antwort'] += f'  {callback.data}'
    choice = users_db[user_id]['antwort']
    tic_dict = await state.get_data()
    a_znachenie = tic_dict['A']
    b_znachenie = tic_dict['B']
    c_znachenie = tic_dict['C']
    send_button = send_button1  # Это название кнопки "ОТПРАВИТЬ"
    enter = f'{process_antwort} {choice}'
    await callback.message.edit_text(
        text=enter,
        reply_markup=abc_builder(a_znachenie, b_znachenie, c_znachenie, send_button))
    await callback.answer()


@cb_router.callback_query(SEND_FILTER())
async def verify_antwort(callback: CallbackQuery, state:FSMContext):
    print("verify_antwort works !\n")
    user_id = callback.from_user.id
    tic_dict = await state.get_data() #  Получаю словарь с ответами
    list_index = users_db[user_id]['current_tic_number']  # Порядковый номер в списке

    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['bot_answer']
            await temp_message.delete()
            users_db[user_id]['bot_answer'] = ''

    test_list = ['🔴', '🟡', '🟢']
    s = ''
    for k, data in enumerate((tic_dict['A'], tic_dict['B'], tic_dict['C']), 0):
        if not data:
            s+= test_list[k]
    user_answer = s

    print('user_answer = ', user_answer)

    current_ticket_id = users_db[user_id]['tik_nummer']  # Получаю уникальный номер билета
    tick_instance = tickets_dict[current_ticket_id]
    right_answer = tick_instance['right_answer']
    print('right_answer = ', right_answer)

    if user_answer == right_answer:
        otwet = f'Вы ответили   {user_answer}\n\n<b>{right}</b>'
        # users_db[user_id]['user_ans'] = otwet  # а это зачем ?
        users_db[user_id]['right_answer'] += 1 #  в db
        await total_increment(user_id)

        if list_index != 29:
            att = await callback.message.answer(otwet,
                                          reply_markup=next_kb)
            users_db[user_id]['bot_answer'] = att
        else:
            await callback.message.answer(otwet,
                                          reply_markup=None)
            bally = users_db[user_id]['right_answer']
            current_state = await state.get_state()
            if current_state != 'FSM_ST:exam':
                stroka = (f'{ticket_finish}\n\nКоличество правильных ответов -   <b>{bally}</b>\n\n{ne_exam_otvet}')
                await callback.message.answer(stroka)
                att = await callback.message.answer('Выбирите действие',
                                                    reply_markup=nach_30_kb)
                users_db[user_id]['bot_answer'] = att
            else:
                await state.set_state(FSM_ST.after_start)
                if bally < 29:
                    stroka = (f'{exam_finish}\n\nКоличество правильных ответов -   <b>{bally}</b>\n\n{exam_ne_sdan}')
                    await callback.message.answer(stroka)
                else:
                    stroka = (f'{exam_finish}\n\nКоличество правильных ответов -   <b>{bally}</b>\n\n{exam_sdan}')
                    await callback.message.answer(stroka)
                # Нужно отменить задачу шедулера
                stop_exam = 'exam'+str(user_id)
                scheduler.remove_job(stop_exam)
            users_db[user_id]['right_answer'] = 0
            users_db[user_id]['current_tic_number'] = 0

    else:
        if tickets_dict[current_ticket_id]['poas']:
            await callback.message.answer(tickets_dict[current_ticket_id]['poas'])
        formated = " ".join(right_answer)
        otwet = f'Вы ответили {user_answer}\n\n<b>{wrong_ans}</b> {formated}'
        if list_index != 29:
            att = await callback.message.answer(otwet,
                                          reply_markup=next_kb)
            users_db[user_id]['bot_answer'] = att
        else:
            await callback.message.answer(otwet,
                                                reply_markup=None)
            bally = users_db[user_id]['right_answer']
            current_state = await state.get_state()
            if current_state != 'FSM_ST:exam':
                stroka = (f'{ticket_finish}\n\nКоличество правильных ответов -   <b>{bally}</b>\n\n{ne_exam_otvet}')
                await callback.message.answer(stroka)
                att = await callback.message.answer('Выбирите действие',
                                                    reply_markup=nach_30_kb)
                users_db[user_id]['bot_answer'] = att

            else:
                await state.set_state(FSM_ST.after_start)
                if bally < 29:
                    stroka = (f'{exam_finish}\n\nКоличество правильных ответов -   <b>{bally}</b>\n\n{exam_ne_sdan}')
                    await callback.message.answer(stroka)
                else:
                    stroka = (f'{exam_finish}\n\nКоличество правильных ответов -   <b>{bally}</b>\n\n{exam_sdan}')
                    await callback.message.answer(stroka)

            users_db[user_id]['right_answer'] = 0
            users_db[user_id]['current_tic_number'] = 0

    users_db[user_id]['user_ans'] = otwet
    await state.update_data(A="🔴", B="🟡", C="🟢")
    users_db[user_id]['antwort'] = ''


@cb_router.callback_query(VYBRATb_BILET_FILTER())
async def vybratb_Bilet(callback: CallbackQuery):
    print("vybratb_Bilet works !\n")
    user_id = callback.from_user.id
    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['bot_answer']
            await temp_message.delete()
        users_db[user_id]['bot_answer'] = ''
    await callback.message.answer(vybrat_bilet)


@cb_router.callback_query(NEW_BILET_FILTER())
async def New_Bilet(callback: CallbackQuery):
    """Эта функция возвращает СЛЕДЮЩИЙ билет из списка билетов"""
    user_id = callback.from_user.id
    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['bot_answer']
            await temp_message.delete()
        users_db[user_id]['bot_answer'] = ''

    print("New_Bilet works !\n")
    users_db[user_id]['bilet_number']+=1
    bilet_id = users_db[user_id]['bilet_number']
    frage_list = get_tickets(bilet_id)
    print('frage list = ', frage_list)
    await insert_new_ticket(user_id, frage_list)
    users_db[user_id]['current_tic_number'] = 0
    key = frage_list[0]
    users_db[user_id]['tik_nummer'] = key  # Уникальный номер вопроса
    num = 1
    ticket = tickets_dict[key]
    if ticket['foto_id']:
        await callback.message.answer_photo(photo=ticket['foto_id'], caption=f'<b>#  {num}</b>  {ticket["desc"]}',
                                   reply_markup=None)
    elif ticket['text_frage']:
        await callback.message.answer(text=f'<b>#  {num}</b>  {ticket["text_frage"]}',
                             reply_markup=None)
    else:
        await callback.message.answer_video(video=ticket['video_id'], caption=f'<b>#  {num}</b>  {ticket["desc"]}',
                                   reply_markup=None)
    att = await callback.message.answer(base_antwort, reply_markup=abc_kb)
    users_db[user_id]['bot_answer'] = att
    await callback.answer()


@cb_router.callback_query(RESET_FILTER())
async def reset_ant(callback: CallbackQuery, state:FSMContext):
    user_id = callback.from_user.id
    print("reset_ant works !\n")
    await state.update_data(A="🔴", B="🟡", C="🟢")
    users_db[user_id]['antwort'] = ''
    await callback.message.edit_text(
        text=base_antwort,
        reply_markup=abc_kb)
    await callback.answer()


@cb_router.callback_query(TZ_FILTER())
async def callback_tz(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    temp_data = users_db[user_id]['bot_answer']
    if temp_data:
        with suppress(TelegramBadRequest):
            temp_message = users_db[user_id]['bot_answer']
            await temp_message.delete()
        users_db[user_id]['bot_answer'] = ''
    if callback.data !='0':
        await state.update_data(my_tz=int(callback.data))
    await callback.message.answer(set_time)
    await callback.answer()






