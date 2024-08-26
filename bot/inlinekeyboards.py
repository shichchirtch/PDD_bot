from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

a_button = InlineKeyboardButton(text='🔴', callback_data='🔴')
b_button = InlineKeyboardButton(text='🟡', callback_data='🟡' )
c_button = InlineKeyboardButton(text='🟢', callback_data='🟢' )

abc_kb = InlineKeyboardMarkup(
            inline_keyboard=[[a_button, b_button, c_button]])

next_ticket = InlineKeyboardButton(text='Следующий вопрос', callback_data='Следующий')

next_kb = InlineKeyboardMarkup(inline_keyboard=[[next_ticket]])

bekom_ticket = InlineKeyboardButton(text='Получить следующий билет', callback_data='Билет')

next_bilet = InlineKeyboardMarkup(inline_keyboard=[[bekom_ticket]])

choose_ticket = InlineKeyboardButton(text='Выбрать билет', callback_data='Выбрать')

nach_30_kb = InlineKeyboardMarkup(inline_keyboard=[[bekom_ticket], [choose_ticket]])

edit_my_ant = InlineKeyboardButton(text='СБРОСИТЬ', callback_data='Сбросить')

button_0 = InlineKeyboardButton(text='У меня столько же', callback_data='0' )
button_1 = InlineKeyboardButton(text='На час больше', callback_data='1' )
button_2 = InlineKeyboardButton(text='На 2 часа больше', callback_data='2' )
button_3 = InlineKeyboardButton(text='На 3 часа больше', callback_data='3' )
button_4 = InlineKeyboardButton(text='На 4 часа больше', callback_data='4' )
button_5 = InlineKeyboardButton(text='На 5 часов больше', callback_data='5' )
button_6 = InlineKeyboardButton(text='На 6 часов больше', callback_data='6' )

tz_kb = InlineKeyboardMarkup(
            inline_keyboard=[[button_0], [button_1],
                             [button_2], [button_3],
                             [button_4], [button_5],
                             [button_6]])

def abc_builder(*args):
    button_array = []
    for button in args:
        # print('button = ', button)
        if button:
            button_array.append(InlineKeyboardButton(text=button, callback_data=button))
    last_button = button_array.pop()
    if button_array:
        return InlineKeyboardMarkup(inline_keyboard=[[*button_array],[edit_my_ant, last_button]])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[[edit_my_ant, last_button]])
