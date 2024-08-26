from aiogram.types import BotCommand
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Функция для настройки кнопки Menu бота
async def set_main_menu(bot):
    # Создаем список с командами и их описанием для кнопки menu
    # bot
    main_menu_commands = [
        BotCommand(command='/get_ticket',
                   description='Получить билет из списка билетов по номеру'),

        BotCommand(command='/help',
                   description='Узнать о моих возможностях'),

        BotCommand(command='/get_30_questions',
                   description='Получить 30 случайных вопросов'),

        BotCommand(command='/exit',
                   description='Вернуться в начало'),

        BotCommand(command='/pruefung',
                   description='Сдать экзамен')
    ]

    await bot.set_my_commands(main_menu_commands)

pre_start_button = KeyboardButton(text='/start')

pre_start_clava = ReplyKeyboardMarkup(
    keyboard=[[pre_start_button]],
    resize_keyboard=True,
    input_field_placeholder='Приятного чтения'
)